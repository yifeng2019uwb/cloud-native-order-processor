package services

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/models"
)

// CircuitBreaker tracks service health and prevents cascading failures
type CircuitBreaker struct {
	serviceName      string
	state            string
	failureCount     int
	successCount     int
	lastFailureTime  time.Time
	failureThreshold int
	timeout          time.Duration
	successThreshold int
	mutex            sync.RWMutex
}

// ProxyService handles forwarding requests to backend services
type ProxyService struct {
	config          *config.Config
	client          *http.Client
	circuitBreakers map[string]*CircuitBreaker
}

// NewProxyService creates a new proxy service
func NewProxyService(cfg *config.Config) *ProxyService {
	circuitBreakers := make(map[string]*CircuitBreaker)

	// Initialize circuit breakers for each service
	services := []string{
		constants.UserService,
		constants.InventoryService,
		constants.OrderService,
		constants.AuthService,
		constants.InsightsService,
	}

	for _, service := range services {
		circuitBreakers[service] = &CircuitBreaker{
			serviceName:      service,
			state:            constants.CircuitBreakerStateClosed,
			failureCount:     0,
			successCount:     0,
			failureThreshold: constants.CircuitBreakerFailureThreshold,
			timeout:          constants.CircuitBreakerTimeout,
			successThreshold: constants.CircuitBreakerSuccessThreshold,
		}
	}

	return &ProxyService{
		config:          cfg,
		client:          &http.Client{Timeout: constants.DefaultTimeout},
		circuitBreakers: circuitBreakers,
	}
}

// ProxyRequest forwards a request to a backend service with circuit breaker protection
func (p *ProxyService) ProxyRequest(ctx context.Context, proxyReq *models.ProxyRequest) (*http.Response, error) {
	// Get circuit breaker for the target service
	cb, exists := p.circuitBreakers[proxyReq.TargetService]
	if !exists {
		return nil, fmt.Errorf("no circuit breaker found for service: %s", proxyReq.TargetService)
	}

	// Check if circuit breaker allows the request
	if !cb.CanExecute() {
		return nil, fmt.Errorf("circuit breaker is open for service %s (state: %s, failures: %d)",
			proxyReq.TargetService, cb.GetState(), cb.GetFailureCount())
	}

	// Build target URL
	targetURL, err := p.buildTargetURL(proxyReq)
	if err != nil {
		cb.RecordFailure()
		return nil, fmt.Errorf("failed to build target URL: %w", err)
	}

	// Create HTTP request
	req, err := p.createHTTPRequest(ctx, proxyReq, targetURL)
	if err != nil {
		cb.RecordFailure()
		return nil, fmt.Errorf("failed to create HTTP request: %w", err)
	}

	// Forward request to backend service
	resp, err := p.client.Do(req)
	if err != nil {
		cb.RecordFailure()
		return nil, fmt.Errorf("backend service request failed: %w", err)
	}

	// Check if response indicates failure (5xx status codes)
	if resp.StatusCode >= 500 {
		cb.RecordFailure()
		return resp, nil // Return response even for 5xx errors
	}

	// Record success for 2xx and 4xx status codes
	cb.RecordSuccess()
	return resp, nil
}

// buildTargetURL constructs the target URL for the backend service
func (p *ProxyService) buildTargetURL(proxyReq *models.ProxyRequest) (string, error) {
	var baseURL string

	switch proxyReq.TargetService {
	case constants.UserService:
		baseURL = p.config.Services.UserService
	case constants.InventoryService:
		baseURL = p.config.Services.InventoryService
	case constants.OrderService:
		baseURL = p.config.Services.OrderService
	case constants.AuthService:
		baseURL = p.config.Services.AuthService
	case constants.InsightsService:
		baseURL = p.config.Services.InsightsService
	default:
		return "", fmt.Errorf("unknown target service: %s", proxyReq.TargetService)
	}

	// Combine base URL with target path
	targetURL := baseURL + proxyReq.TargetPath

	// Add query parameters if present
	if len(proxyReq.QueryParams) > 0 {
		u, err := url.Parse(targetURL)
		if err != nil {
			return "", fmt.Errorf("failed to parse target URL: %w", err)
		}

		q := u.Query()
		for key, value := range proxyReq.QueryParams {
			q.Set(key, value)
		}
		u.RawQuery = q.Encode()
		targetURL = u.String()
	}

	return targetURL, nil
}

// createHTTPRequest creates an HTTP request for the backend service
func (p *ProxyService) createHTTPRequest(ctx context.Context, proxyReq *models.ProxyRequest, targetURL string) (*http.Request, error) {
	var body io.Reader

	// Handle request body
	if proxyReq.Body != nil {
		bodyBytes, err := json.Marshal(proxyReq.Body)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal request body: %w", err)
		}
		body = bytes.NewBuffer(bodyBytes)
	}

	// Create HTTP request
	req, err := http.NewRequestWithContext(ctx, proxyReq.Method, targetURL, body)
	if err != nil {
		return nil, fmt.Errorf("failed to create HTTP request: %w", err)
	}

	// Copy headers from original request
	for key, value := range proxyReq.Headers {
		req.Header.Set(key, value)
	}

	// Add request ID header for distributed tracing
	if proxyReq.Context != nil && proxyReq.Context.RequestID != "" {
		req.Header.Set(constants.XRequestIDHeader, proxyReq.Context.RequestID)
	}

	// Add user context headers if user is authenticated
	if proxyReq.Context != nil && proxyReq.Context.User != nil && proxyReq.Context.User.Username != "" {
		req.Header.Set(constants.XUserIDHeader, proxyReq.Context.User.Username)
		req.Header.Set(constants.XUserRoleHeader, proxyReq.Context.User.Role)
		req.Header.Set(constants.XAuthenticatedHeader, constants.HeaderValueTrue)
	}

	// Add source and auth service headers for backend service validation
	req.Header.Set(constants.XSourceHeader, constants.HeaderValueGateway)
	req.Header.Set(constants.XAuthServiceHeader, "auth-service")

	// Set content type if not present
	if req.Header.Get("Content-Type") == "" && proxyReq.Body != nil {
		req.Header.Set("Content-Type", constants.ContentTypeJSON)
	}

	return req, nil
}

// stripAPIPrefix removes the API prefix from the path
// e.g., "/api/v1/auth/login" -> "/login"
func (p *ProxyService) stripAPIPrefix(path, prefix string) string {
	if strings.HasPrefix(path, prefix) {
		return strings.TrimPrefix(path, prefix)
	}
	return path
}

// GetRouteConfig returns the route configuration for a given path
func (p *ProxyService) GetRouteConfig(path string) (*constants.RouteConfig, bool) {
	config, exists := constants.RouteConfigs[path]
	if !exists {
		return nil, false
	}
	return &config, true
}

// GetTargetService determines the target service for a given path
func (p *ProxyService) GetTargetService(path string) string {
	switch {
	case strings.HasPrefix(path, constants.APIV1AuthPath):
		return constants.UserService
	case strings.HasPrefix(path, constants.APIV1InventoryPath):
		return constants.InventoryService
	case strings.HasPrefix(path, constants.APIV1OrderPath):
		return constants.OrderService
	case strings.HasPrefix(path, constants.APIV1PortfolioPath):
		return constants.UserService // Portfolio is handled by user service
	case strings.HasPrefix(path, constants.APIV1AssetBalanceByID):
		return constants.UserService // Asset balance is handled by user service
	case strings.HasPrefix(path, constants.APIV1BalancePath):
		return constants.UserService // Balance is handled by user service
	case strings.HasPrefix(path, constants.APIV1AssetPath):
		return constants.OrderService // Asset balances handled by order service
	case strings.HasPrefix(path, constants.APIV1InsightsPath):
		return constants.InsightsService // Insights service
	default:
		return ""
	}
}

// Circuit breaker methods

// CanExecute checks if the circuit breaker allows the request to proceed
func (cb *CircuitBreaker) CanExecute() bool {
	cb.mutex.RLock()
	defer cb.mutex.RUnlock()

	switch cb.state {
	case constants.CircuitBreakerStateClosed:
		return true
	case constants.CircuitBreakerStateOpen:
		// Check if timeout has passed to transition to half-open
		if time.Since(cb.lastFailureTime) >= cb.timeout {
			cb.mutex.RUnlock()
			cb.mutex.Lock()
			cb.state = constants.CircuitBreakerStateHalfOpen
			cb.successCount = 0
			cb.mutex.Unlock()
			cb.mutex.RLock()
			return true
		}
		return false
	case constants.CircuitBreakerStateHalfOpen:
		return true
	default:
		return false
	}
}

// RecordSuccess records a successful request
func (cb *CircuitBreaker) RecordSuccess() {
	cb.mutex.Lock()
	defer cb.mutex.Unlock()

	cb.successCount++

	// If in half-open state and success threshold reached, close the circuit
	if cb.state == constants.CircuitBreakerStateHalfOpen && cb.successCount >= cb.successThreshold {
		cb.state = constants.CircuitBreakerStateClosed
		cb.failureCount = 0
		cb.successCount = 0
	}
}

// RecordFailure records a failed request
func (cb *CircuitBreaker) RecordFailure() {
	cb.mutex.Lock()
	defer cb.mutex.Unlock()

	cb.failureCount++
	cb.lastFailureTime = time.Now()

	// If failure threshold reached, open the circuit
	if cb.failureCount >= cb.failureThreshold {
		cb.state = constants.CircuitBreakerStateOpen
	}
}

// GetState returns the current circuit breaker state
func (cb *CircuitBreaker) GetState() string {
	cb.mutex.RLock()
	defer cb.mutex.RUnlock()
	return cb.state
}

// GetFailureCount returns the current failure count
func (cb *CircuitBreaker) GetFailureCount() int {
	cb.mutex.RLock()
	defer cb.mutex.RUnlock()
	return cb.failureCount
}

// GetCircuitBreakerStatus returns the status of all circuit breakers
func (p *ProxyService) GetCircuitBreakerStatus() map[string]map[string]interface{} {
	status := make(map[string]map[string]interface{})

	for serviceName, cb := range p.circuitBreakers {
		status[serviceName] = map[string]interface{}{
			constants.CircuitBreakerFieldState:        cb.GetState(),
			constants.CircuitBreakerFieldFailureCount: cb.GetFailureCount(),
			constants.CircuitBreakerFieldServiceName:  cb.serviceName,
		}
	}

	return status
}

// Phase 3: Advanced features (Future - simple comments)
// - Service discovery integration
// - Load balancing
// - Advanced monitoring and metrics
// - Retry logic with exponential backoff
// - Advanced caching strategies
