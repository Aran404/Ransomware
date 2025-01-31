package crypt

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"crypto/x509"
	"encoding/base64"
	"encoding/pem"
	"fmt"
	"log"
	"strings"
)

func padBase64(encoded string) string {
	missingPadding := len(encoded) % 4
	if missingPadding > 0 {
		encoded += strings.Repeat("=", 4-missingPadding)
	}
	return encoded
}

func FromPEM(pemData []byte) (*RSA, error) {
	block, _ := pem.Decode(pemData)
	if block == nil {
		return nil, fmt.Errorf("failed to parse PEM block")
	}

	priv, err := x509.ParsePKCS1PrivateKey(block.Bytes)
	if err != nil {
		return nil, err
	}

	return &RSA{
		PublicKey:  &priv.PublicKey,
		PrivateKey: priv,
	}, nil
}

func NewRSA(keySize int) (*RSA, error) {
	privateKey, err := rsa.GenerateKey(rand.Reader, keySize)
	if err != nil {
		return nil, err
	}

	return &RSA{
		PublicKey:  &privateKey.PublicKey,
		PrivateKey: privateKey,
	}, nil
}

func (r *RSA) ExportPEM() (pub []byte, priv []byte, err error) {
	pub = x509.MarshalPKCS1PublicKey(r.PublicKey)
	priv = x509.MarshalPKCS1PrivateKey(r.PrivateKey)
	priv = pem.EncodeToMemory(&pem.Block{Type: "RSA PRIVATE KEY", Bytes: priv})
	pub = pem.EncodeToMemory(&pem.Block{Type: "RSA PUBLIC KEY", Bytes: pub})
	return
}

func (r *RSA) Encrypt(message string) ([]byte, error) {
	msg, err := rsa.EncryptOAEP(sha256.New(), rand.Reader, r.PublicKey, []byte(message), nil)
	if err != nil {
		return nil, err
	}
	b := []byte{}
	base64.StdEncoding.Encode(b, msg)
	return b, nil
}

func (r *RSA) Decrypt(cipher string) ([]byte, error) {
	cipher = padBase64(cipher)
	decoded, err := base64.StdEncoding.DecodeString(cipher)
	if err != nil {
		return nil, err
	}

	msg, err := rsa.DecryptOAEP(sha256.New(), rand.Reader, r.PrivateKey, []byte(decoded), nil)
	if err != nil {
		return nil, err
	}

	return msg, nil
}
