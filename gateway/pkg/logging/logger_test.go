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

	expectedMessage := "Gateway starting [version=1.0.0]"
	if entry.Message != expectedMessage {
		t.Errorf("Expected message '%s', got '%s'", expectedMessage, entry.Message)
	}
}

func TestLogErrorHandling(t *testing.T) {
	const (
		testUser         = ""
		testInfoMessage  = "Test with invalid JSON"
		testErrorMessage = "Test error with invalid JSON"
	)

	logger := NewBaseLogger(GATEWAY)

	// Test log function with invalid JSON (by using a channel which can't be marshaled)
	// This tests the error path in the log function
	invalidExtra := map[string]interface{}{
		"channel": make(chan int), // Channels can't be JSON marshaled
	}

	// Should not panic, just log an error
	logger.Info(REQUEST_START, testInfoMessage, testUser, invalidExtra)
	logger.Error(AUTH_FAILURE, testErrorMessage, testUser, invalidExtra)
}

func TestLogEntryAllFields(t *testing.T) {
	const (
		testRequestID    = "req-test-123"
		testUser         = "testuser"
		testUser1        = "user1"
		testUser2        = "user2"
		testFullMessage  = "Full test message"
		testNoExtraMsg   = "Message without extra"
		testNoUserMsg    = "Message without user"
		testDebugMessage = "Debug message"
		testWarningMsg   = "Warning message"
		testErrorMessage = "Error message"
		testValue        = "value"
		testErrorCode    = "AUTH_001"
	)

	const (
		testMethod = "GET"
		testPath   = "/api/v1/test"
		testStatus = 200
	)

	logger := NewBaseLogger(GATEWAY)
	logger.SetRequestID(testRequestID)

	testCases := []struct {
		name    string
		action  LogActions
		message string
		user    string
		extra   map[string]interface{}
		logFunc func(LogActions, string, string, map[string]interface{})
	}{
		{
			name:    "Info with all fields populated",
			action:  REQUEST_START,
			message: testFullMessage,
			user:    testUser,
			extra: map[string]interface{}{
				"method": testMethod,
				"path":   testPath,
				"status": testStatus,
			},
			logFunc: logger.Info,
		},
		{
			name:    "Info with nil extra",
			action:  REQUEST_START,
			message: testNoExtraMsg,
			user:    testUser,
			extra:   nil,
			logFunc: logger.Info,
		},
		{
			name:    "Info with empty user",
			action:  REQUEST_START,
			message: testNoUserMsg,
			user:    "",
			extra: map[string]interface{}{
				"test": testValue,
			},
			logFunc: logger.Info,
		},
		{
			name:    "Debug message",
			action:  HEALTH,
			message: testDebugMessage,
			user:    "",
			extra:   nil,
			logFunc: logger.Debug,
		},
		{
			name:    "Warning message",
			action:  REQUEST_END,
			message: testWarningMsg,
			user:    testUser1,
			extra:   nil,
			logFunc: logger.Warning,
		},
		{
			name:    "Error message",
			action:  AUTH_FAILURE,
			message: testErrorMessage,
			user:    testUser2,
			extra: map[string]interface{}{
				"error_code": testErrorCode,
			},
			logFunc: logger.Error,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			tc.logFunc(tc.action, tc.message, tc.user, tc.extra)
			// Test should not panic
		})
	}
}

func TestJSONFormatterFormatError(t *testing.T) {
	const (
		testTimestamp = "2025-08-29T15:00:00Z"
		testMessage   = "Test"
		testValidData = "data"
	)

	var (
		testService = "gateway"
	)

	formatter := NewJSONFormatter()

	entry := LogEntry{
		Timestamp: testTimestamp,
		Level:     INFO,
		Service:   testService,
		Action:    REQUEST_START,
		Message:   testMessage,
	}

	jsonStr, err := formatter.Format(entry)
	if err != nil {
		t.Errorf("Format should not fail with valid entry: %v", err)
	}
	if jsonStr == "" {
		t.Error("Format should return non-empty string")
	}

	// Verify it's valid JSON
	var parsed LogEntry
	if err := json.Unmarshal([]byte(jsonStr), &parsed); err != nil {
		t.Errorf("Formatted output should be valid JSON: %v", err)
	}
}
