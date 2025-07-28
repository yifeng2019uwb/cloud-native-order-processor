package models

import (
	"encoding/json"
	"testing"
	"time"

	"order-processor-gateway/pkg/constants"
)

func TestAPIResponseSuccess(t *testing.T) {
	// Create a success response
	response := APIResponse{
		Success:   true,
		Data:      map[string]string{"user_id": "123", "name": "John"},
		Message:   "User created successfully",
		Timestamp: time.Now(),
		RequestID: "test-request-id",
	}

	// Test basic fields
	if !response.Success {
		t.Error("Success should be true")
	}
	if response.Data == nil {
		t.Error("Data should not be nil")
	}
	if response.Message != "User created successfully" {
		t.Errorf("Expected message 'User created successfully', got %s", response.Message)
	}
	if response.RequestID != "test-request-id" {
		t.Errorf("Expected request ID 'test-request-id', got %s", response.RequestID)
	}

	// Test JSON marshaling
	jsonData, err := json.Marshal(response)
	if err != nil {
		t.Errorf("Failed to marshal response: %v", err)
	}

	// Verify JSON structure
	var unmarshaled APIResponse
	err = json.Unmarshal(jsonData, &unmarshaled)
	if err != nil {
		t.Errorf("Failed to unmarshal response: %v", err)
	}

	if unmarshaled.Success != response.Success {
		t.Error("Success field should be preserved in JSON")
	}
}

func TestAPIResponseError(t *testing.T) {
	// Create an error response
	response := APIResponse{
		Success:   false,
		Error:     constants.ErrorCodeValidation,
		Message:   "Invalid input data",
		Timestamp: time.Now(),
		RequestID: "test-request-id",
	}

	// Test basic fields
	if response.Success {
		t.Error("Success should be false")
	}
	if response.Error != constants.ErrorCodeValidation {
		t.Errorf("Expected error code '%s', got %s", constants.ErrorCodeValidation, response.Error)
	}
	if response.Message != "Invalid input data" {
		t.Errorf("Expected message 'Invalid input data', got %s", response.Message)
	}

	// Test that Data field is omitted in JSON when nil
	jsonData, err := json.Marshal(response)
	if err != nil {
		t.Errorf("Failed to marshal error response: %v", err)
	}

	// Check that "data" field is not present in JSON
	var jsonMap map[string]interface{}
	err = json.Unmarshal(jsonData, &jsonMap)
	if err != nil {
		t.Errorf("Failed to unmarshal to map: %v", err)
	}

	if _, exists := jsonMap["data"]; exists {
		t.Error("Data field should be omitted in JSON when nil")
	}
}

func TestAPIResponseEmptyFields(t *testing.T) {
	// Test response with minimal fields
	response := APIResponse{
		Success:   true,
		Timestamp: time.Now(),
	}

	// Test that optional fields are properly handled
	if response.Data != nil {
		t.Error("Data should be nil when not set")
	}
	if response.Error != "" {
		t.Error("Error should be empty when not set")
	}
	if response.Message != "" {
		t.Error("Message should be empty when not set")
	}
	if response.RequestID != "" {
		t.Error("RequestID should be empty when not set")
	}

	// Test JSON marshaling with empty fields
	jsonData, err := json.Marshal(response)
	if err != nil {
		t.Errorf("Failed to marshal minimal response: %v", err)
	}

	// Verify that empty fields are omitted
	var jsonMap map[string]interface{}
	err = json.Unmarshal(jsonData, &jsonMap)
	if err != nil {
		t.Errorf("Failed to unmarshal to map: %v", err)
	}

	// Check that empty fields are omitted
	if _, exists := jsonMap["data"]; exists {
		t.Error("Empty data field should be omitted")
	}
	if _, exists := jsonMap["error"]; exists {
		t.Error("Empty error field should be omitted")
	}
	if _, exists := jsonMap["message"]; exists {
		t.Error("Empty message field should be omitted")
	}
	if _, exists := jsonMap["request_id"]; exists {
		t.Error("Empty request_id field should be omitted")
	}
}

func TestErrorInfo(t *testing.T) {
	// Create error info
	errorInfo := ErrorInfo{
		Code:    constants.ErrorCodeValidation,
		Message: "Email format is invalid",
		Details: "Email must contain @ symbol",
	}

	// Test basic fields
	if errorInfo.Code != constants.ErrorCodeValidation {
		t.Errorf("Expected error code '%s', got %s", constants.ErrorCodeValidation, errorInfo.Code)
	}
	if errorInfo.Message != "Email format is invalid" {
		t.Errorf("Expected message 'Email format is invalid', got %s", errorInfo.Message)
	}
	if errorInfo.Details != "Email must contain @ symbol" {
		t.Errorf("Expected details 'Email must contain @ symbol', got %s", errorInfo.Details)
	}

	// Test JSON marshaling
	jsonData, err := json.Marshal(errorInfo)
	if err != nil {
		t.Errorf("Failed to marshal error info: %v", err)
	}

	// Verify JSON structure
	var unmarshaled ErrorInfo
	err = json.Unmarshal(jsonData, &unmarshaled)
	if err != nil {
		t.Errorf("Failed to unmarshal error info: %v", err)
	}

	if unmarshaled.Code != errorInfo.Code {
		t.Error("Code field should be preserved in JSON")
	}
	if unmarshaled.Message != errorInfo.Message {
		t.Error("Message field should be preserved in JSON")
	}
	if unmarshaled.Details != errorInfo.Details {
		t.Error("Details field should be preserved in JSON")
	}
}

func TestErrorInfoWithoutDetails(t *testing.T) {
	// Test error info without details
	errorInfo := ErrorInfo{
		Code:    constants.ErrorCodeAuthentication,
		Message: "Invalid credentials",
	}

	// Test that details is empty
	if errorInfo.Details != "" {
		t.Error("Details should be empty when not set")
	}

	// Test JSON marshaling
	jsonData, err := json.Marshal(errorInfo)
	if err != nil {
		t.Errorf("Failed to marshal error info without details: %v", err)
	}

	// Verify that details field is omitted
	var jsonMap map[string]interface{}
	err = json.Unmarshal(jsonData, &jsonMap)
	if err != nil {
		t.Errorf("Failed to unmarshal to map: %v", err)
	}

	if _, exists := jsonMap["details"]; exists {
		t.Error("Empty details field should be omitted")
	}
}
