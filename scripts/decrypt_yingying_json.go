package main

import (
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

var insertionPositions = []int{0, 7, 20, 33, 40, 47, 59, 66, 76, 89, 99, 127}

func decrypt(encoded string) ([]byte, error) {
	work := []byte(strings.TrimSpace(encoded))
	chunks := make([][]byte, 0, len(insertionPositions))
	for index := len(insertionPositions) - 1; index >= 0; index-- {
		position := insertionPositions[index]
		if position+4 > len(work) {
			return nil, fmt.Errorf("payload too short at insertion position %d", position)
		}
		chunk := append([]byte(nil), work[position:position+4]...)
		chunks = append(chunks, chunk)
		work = append(work[:position], work[position+4:]...)
	}
	keyNonce := make([]byte, 0, 48)
	for index := len(chunks) - 1; index >= 0; index-- {
		keyNonce = append(keyNonce, chunks[index]...)
	}
	if len(keyNonce) != 48 {
		return nil, fmt.Errorf("invalid key/nonce length: %d", len(keyNonce))
	}
	sealed, err := base64.StdEncoding.DecodeString(string(work))
	if err != nil {
		return nil, fmt.Errorf("base64 decode: %w", err)
	}
	block, err := aes.NewCipher(keyNonce[:32])
	if err != nil {
		return nil, fmt.Errorf("AES key: %w", err)
	}
	var gcm cipher.AEAD
	gcm, err = cipher.NewGCMWithNonceSize(block, 16)
	if err != nil {
		return nil, fmt.Errorf("GCM nonce: %w", err)
	}
	plaintext, err := gcm.Open(nil, keyNonce[32:], sealed, nil)
	if err != nil {
		return nil, fmt.Errorf("GCM authentication: %w", err)
	}
	if !json.Valid(plaintext) {
		return nil, fmt.Errorf("decrypted payload is not valid JSON")
	}
	return plaintext, nil
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: decrypt_yingying_json <encrypted-draft-json>")
		os.Exit(2)
	}
	encoded, err := os.ReadFile(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	plaintext, err := decrypt(string(encoded))
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if _, err := os.Stdout.Write(plaintext); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
