package utils

import (
	"github.com/google/uuid"
)

// GenerateRequestID creates a unique request identifier using UUID v4
func GenerateRequestID() string {
	return uuid.New().String()
}

// IsValidRequestID checks if a request ID is a valid UUID
func IsValidRequestID(requestID string) bool {
	_, err := uuid.Parse(requestID)
	return err == nil
}
