package logging

import (
	"encoding/json"
	"testing"
)

func TestNewBaseLogger(t *testing.T) {
	logger := NewBaseLogger(GATEWAY)

	if logger.service != "gateway" {
		t.Errorf("Expected service to be 'gateway', got '%s'", logger.service)
	}
}

func TestSetRequestID(t *testing.T) {
	logger := NewBaseLogger(GATEWAY)
	requestID := "test-request-123"

	logger.SetRequestID(requestID)

	if logger.requestID != requestID {
		t.Errorf("Expected request ID to be '%s', got '%s'", requestID, logger.requestID)
	}
}

func TestLogEntryStructure(t *testing.T) {
	logger := NewBaseLogger(GATEWAY)
	logger.SetRequestID("test-123")

	// Capture stdout to test log output
	// This is a basic test - in real usage we'd use a more sophisticated approach

	// Test that logger methods don't panic
	logger.Info(REQUEST_START, "Test message", "testuser", map[string]interface{}{
		"test": "value",
	})

	logger.Error(AUTH_FAILURE, "Test error", "testuser", map[string]interface{}{
		"error": "test error",
	})

	logger.Warning(REQUEST_END, "Test warning", "testuser", nil)

	logger.Debug(HEALTH, "Test debug", "", nil)
}

func TestJSONFormatter(t *testing.T) {
	formatter := NewJSONFormatter()

	entry := LogEntry{
		Timestamp: "2025-08-29T15:00:00Z",
		Level:     INFO,
		Service:   "gateway",
		Action:    REQUEST_START,
		Message:   "Test message",
	}

	jsonStr, err := formatter.Format(entry)
	if err != nil {
		t.Errorf("Failed to format log entry: %v", err)
	}

	// Verify it's valid JSON
	var parsedEntry LogEntry
	err = json.Unmarshal([]byte(jsonStr), &parsedEntry)
	if err != nil {
		t.Errorf("Failed to parse formatted JSON: %v", err)
	}

	if parsedEntry.Message != "Test message" {
		t.Errorf("Expected message 'Test message', got '%s'", parsedEntry.Message)
	}
}

func TestCreateRequestLog(t *testing.T) {
	formatter := NewJSONFormatter()

	entry := formatter.CreateRequestLog(INFO, REQUEST_START, "Test request", "testuser", "req-123", map[string]interface{}{
		"method": "GET",
		"path":   "/test",
	})

	if entry.Service != "gateway" {
		t.Errorf("Expected service 'gateway', got '%s'", entry.Service)
	}

	if entry.RequestID != "req-123" {
		t.Errorf("Expected request ID 'req-123', got '%s'", entry.RequestID)
	}

	if entry.User != "testuser" {
		t.Errorf("Expected user 'testuser', got '%s'", entry.User)
	}
}

func TestCreateSystemLog(t *testing.T) {
	formatter := NewJSONFormatter()

	entry := formatter.CreateSystemLog(INFO, STARTUP, "Gateway starting", map[string]interface{}{
		"version": "1.0.0",
	})

	if entry.Service != "gateway" {
		t.Errorf("Expected service 'gateway', got '%s'", entry.Service)
	}

	if entry.Action != STARTUP {
		t.Errorf("Expected action STARTUP, got %v", entry.Action)
	}

	if entry.Message != "Gateway starting" {
		t.Errorf("Expected message 'Gateway starting', got '%s'", entry.Message)
	}
}
