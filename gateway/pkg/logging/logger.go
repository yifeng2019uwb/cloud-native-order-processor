package logging

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"time"
)

// LogEntry represents a structured log entry
type LogEntry struct {
	Timestamp string                 `json:"timestamp"`
	Level     LogLevel               `json:"level"`
	Service   string                 `json:"service"`
	RequestID string                 `json:"request_id,omitempty"`
	Action    LogActions             `json:"action"`
	Message   string                 `json:"message"`
	User      string                 `json:"user,omitempty"`
	Extra     map[string]interface{} `json:"extra,omitempty"`
}

// BaseLogger represents the main logging interface
type BaseLogger struct {
	service   string
	requestID string
}

// NewBaseLogger creates a new BaseLogger instance
func NewBaseLogger(service Loggers) *BaseLogger {
	return &BaseLogger{
		service: string(service),
	}
}

// SetRequestID sets the request ID for correlation
func (l *BaseLogger) SetRequestID(requestID string) {
	l.requestID = requestID
}

// Info logs an informational message
func (l *BaseLogger) Info(action LogActions, message string, user string, extra map[string]interface{}) {
	l.log(INFO, action, message, user, extra)
}

// Error logs an error message
func (l *BaseLogger) Error(action LogActions, message string, user string, extra map[string]interface{}) {
	l.log(ERROR, action, message, user, extra)
}

// Warning logs a warning message
func (l *BaseLogger) Warning(action LogActions, message string, user string, extra map[string]interface{}) {
	l.log(WARN, action, message, user, extra)
}

// Debug logs a debug message
func (l *BaseLogger) Debug(action LogActions, message string, user string, extra map[string]interface{}) {
	l.log(DEBUG, action, message, user, extra)
}

// log is the internal logging method
func (l *BaseLogger) log(level LogLevel, action LogActions, message string, user string, extra map[string]interface{}) {
	entry := LogEntry{
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Level:     level,
		Service:   l.service,
		RequestID: l.requestID,
		Action:    action,
		Message:   message,
		User:      user,
		Extra:     extra,
	}

	// Marshal to JSON
	jsonData, err := json.Marshal(entry)
	if err != nil {
		// Fallback to standard log if JSON marshaling fails
		log.Printf("Failed to marshal log entry: %v", err)
		return
	}

	// Write to stdout for Kubernetes compatibility
	fmt.Fprintf(os.Stdout, "%s\n", string(jsonData))
}
