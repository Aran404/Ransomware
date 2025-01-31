package crypt

import "crypto/rsa"

const (
	DEFAULT_KEY_SIZE = 4096
)

type RSA struct {
	PublicKey  *rsa.PublicKey
	PrivateKey *rsa.PrivateKey
}
