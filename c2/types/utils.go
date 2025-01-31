package types

import (
	"fmt"
	"io"
	"math/rand"
	"os"
	"strings"
	"time"
)

const (
	CHAR_LIST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
)

func RandString() string {
	r := rand.New(rand.NewSource(time.Now().UnixNano()))
	var s strings.Builder
	for i := 0; i < 64; i++ {
		i := r.Int63n(int64(len(CHAR_LIST)))
		s.WriteByte(CHAR_LIST[i])
	}
	return s.String()
}

func LoadPEMFile(typeString string) ([]byte, error) {
	file, err := os.Open(fmt.Sprintf("%s.pem", typeString))
	if err != nil {
		return nil, err
	}
	defer file.Close()

	pem, err := io.ReadAll(file)
	if err != nil {
		return nil, err
	}

	return pem, nil
}
