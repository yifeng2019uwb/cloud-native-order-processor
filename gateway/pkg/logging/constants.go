package logging

// LogActions represents the type of action being logged
type LogActions string

const (
	// Request lifecycle actions
	REQUEST_START LogActions = "request_start"
	REQUEST_END   LogActions = "request_end"

	// Authentication actions (only failures, Gateway doesn't handle success)
	AUTH_FAILURE LogActions = "auth_failure"

	// System actions
	STARTUP  LogActions = "startup"
	SHUTDOWN LogActions = "shutdown"
	HEALTH   LogActions = "health"

	// Backend/proxy actions (service catches and logs; metrics record separately)
	PROXY_FAILURE LogActions = "proxy_failure" // connection/timeout to backend
	BACKEND_5XX   LogActions = "backend_5xx"   // backend returned 5xx
)

// Loggers represents the service identifier for logging
type Loggers string

const (
	// Service identifiers
	GATEWAY   Loggers = "gateway"
	AUTH      Loggers = "auth"
	USER      Loggers = "user"
	ORDER     Loggers = "order"
	INVENTORY Loggers = "inventory"

	// Specialized loggers
	AUDIT Loggers = "audit"
)

// LogLevel represents the logging level
type LogLevel string

const (
	DEBUG LogLevel = "DEBUG"
	INFO  LogLevel = "INFO"
	WARN  LogLevel = "WARN"
	ERROR LogLevel = "ERROR"
)
