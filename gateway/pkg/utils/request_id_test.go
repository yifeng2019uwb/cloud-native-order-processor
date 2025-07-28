package utils

import (
	"testing"
)

func TestGenerateRequestID(t *testing.T) {
	// Generate multiple request IDs
	id1 := GenerateRequestID()
	id2 := GenerateRequestID()
	id3 := GenerateRequestID()

	// Check that they are valid UUIDs
	if !IsValidRequestID(id1) {
		t.Errorf("Generated request ID is not a valid UUID: %s", id1)
	}
	if !IsValidRequestID(id2) {
		t.Errorf("Generated request ID is not a valid UUID: %s", id2)
	}
	if !IsValidRequestID(id3) {
		t.Errorf("Generated request ID is not a valid UUID: %s", id3)
	}

	// Check that they are unique
	if id1 == id2 || id1 == id3 || id2 == id3 {
		t.Error("Generated request IDs are not unique")
	}

	// Check UUID format (should be 36 characters with dashes)
	if len(id1) != 36 {
		t.Errorf("Request ID should be 36 characters, got %d: %s", len(id1), id1)
	}
}

func TestIsValidRequestID(t *testing.T) {
	// Test valid UUID
	validID := "550e8400-e29b-41d4-a716-446655440000"
	if !IsValidRequestID(validID) {
		t.Errorf("Valid UUID should be accepted: %s", validID)
	}

	// Test invalid UUID
	invalidID := "not-a-uuid"
	if IsValidRequestID(invalidID) {
		t.Errorf("Invalid UUID should be rejected: %s", invalidID)
	}
}
