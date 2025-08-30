package logging

import (
	"encoding/json"
	"time"
)

// JSONFormatter provides basic JSON formatting for Gateway logs
type JSONFormatter struct{}

// NewJSONFormatter creates a new JSON formatter
func NewJSONFormatter() *JSONFormatter {
	return &JSONFormatter{}
}

// Format formats a log entry into JSON string
func (f *JSONFormatter) Format(entry LogEntry) (string, error) {
	jsonData, err := json.Marshal(entry)
	if err != nil {
		return "", err
	}
	return string(jsonData), nil
}

// CreateRequestLog creates a log entry for HTTP requests
func (f *JSONFormatter) CreateRequestLog(level LogLevel, action LogActions, message string,
	user string, requestID string, extra map[string]interface{}) LogEntry {

	return LogEntry{
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Level:     level,
		Service:   "gateway",
		RequestID: requestID,
		Action:    action,
		Message:   message,
		User:      user,
		Extra:     extra,
	}
}

// CreateSystemLog creates a log entry for system events
func (f *JSONFormatter) CreateSystemLog(level LogLevel, action LogActions, message string,
	extra map[string]interface{}) LogEntry {

	return LogEntry{
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Level:     level,
		Service:   "gateway",
		Action:    action,
		Message:   message,
		Extra:     extra,
	}
}
