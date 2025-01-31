package server

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net"
	"net/http"
	"strings"

	"github.com/Aran404/Ransomware/c2/types"
)

func ParseJSON(r *http.Request, v interface{}) error {
	data, err := io.ReadAll(r.Body)
	if err != nil {
		return err
	}

	if r.Header.Get("Content-Type") != "application/json" {
		return types.ErrNotJSON
	}

	return json.Unmarshal(data, v)
}

func SendJSON(w http.ResponseWriter, v interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(v); err != nil {
		log.Printf("Error encoding response: %v", err)
	}
}

func SendWebhook(uri string, v interface{}) {
	body := new(bytes.Buffer)
	if err := json.NewEncoder(body).Encode(v); err != nil {
		return
	}

	_, err := http.Post(uri, "application/json", body)
	if err != nil {
		log.Printf("Error sending webhook: %v", err)
	}
}

func IsLocalhost(r *http.Request) bool {
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return false
	}
	return host == "127.0.0.1" || host == "::1" || strings.Contains(host, "localhost")
}
