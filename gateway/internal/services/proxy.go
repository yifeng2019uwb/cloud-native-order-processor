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
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/models"
)

// ProxyService handles forwarding requests to backend services
type ProxyService struct {
	config *config.Config
	client *http.Client
}

// NewProxyService creates a new proxy service
func NewProxyService(cfg *config.Config) *ProxyService {
	return &ProxyService{
		config: cfg,
		client: &http.Client{
			Timeout: constants.DefaultTimeout,
		},
	}
}

// ProxyRequest forwards a request to a backend service
// Phase 1: Basic request forwarding with error handling
func (p *ProxyService) ProxyRequest(ctx context.Context, proxyReq *models.ProxyRequest) (*http.Response, error) {
	// Phase 1: Simple request forwarding
	// Phase 2: Add circuit breaker logic
	// Phase 3: Add retry logic and advanced monitoring

	// Build target URL
	targetURL, err := p.buildTargetURL(proxyReq)
	if err != nil {
		return nil, fmt.Errorf("failed to build target URL: %w", err)
	}

	// Create HTTP request
	req, err := p.createHTTPRequest(ctx, proxyReq, targetURL)
	if err != nil {
		return nil, fmt.Errorf("failed to create HTTP request: %w", err)
	}

	// Forward request to backend service
	resp, err := p.client.Do(req)
	if err != nil {
		// Phase 2: Circuit breaker - increment failure count
		return nil, fmt.Errorf("backend service request failed: %w", err)
	}

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

	// Add user context headers if user is authenticated
	if proxyReq.Context != nil && proxyReq.Context.User != nil && proxyReq.Context.User.IsAuthenticated {
		req.Header.Set(constants.XUserIDHeader, proxyReq.Context.User.Username)
		req.Header.Set(constants.XUserRoleHeader, proxyReq.Context.User.Role)
		req.Header.Set(constants.XAuthenticatedHeader, "true")
	}

	// Add source header
	req.Header.Set(constants.XSourceHeader, "gateway")

	// Set content type if not present
	if req.Header.Get("Content-Type") == "" && proxyReq.Body != nil {
		req.Header.Set("Content-Type", constants.ContentTypeJSON)
	}

	return req, nil
}

// ProxyToUserService forwards requests to user service
func (p *ProxyService) ProxyToUserService(ctx context.Context, path string, method string, headers map[string]string, body interface{}) (*http.Response, error) {
	proxyReq := &models.ProxyRequest{
		Method:        method,
		Path:          path,
		Headers:       headers,
		Body:          body,
		TargetService: constants.UserService,
		TargetPath:    p.stripAPIPrefix(path, constants.APIV1AuthPath),
		Context: &models.RequestContext{
			RequestID:   generateRequestID(),
			Timestamp:   time.Now(),
			ServiceName: constants.UserService,
		},
	}

	return p.ProxyRequest(ctx, proxyReq)
}

// ProxyToInventoryService forwards requests to inventory service
func (p *ProxyService) ProxyToInventoryService(ctx context.Context, path string, method string, headers map[string]string, body interface{}) (*http.Response, error) {
	proxyReq := &models.ProxyRequest{
		Method:        method,
		Path:          path,
		Headers:       headers,
		Body:          body,
		TargetService: constants.InventoryService,
		TargetPath:    p.stripAPIPrefix(path, constants.APIV1InventoryPath),
		Context: &models.RequestContext{
			RequestID:   generateRequestID(),
			Timestamp:   time.Now(),
			ServiceName: constants.InventoryService,
		},
	}

	return p.ProxyRequest(ctx, proxyReq)
}

// ProxyToOrderService forwards requests to order service
func (p *ProxyService) ProxyToOrderService(ctx context.Context, path string, method string, headers map[string]string, body interface{}) (*http.Response, error) {
	var targetPath string

	// Handle different path prefixes for order service
	switch {
	case strings.HasPrefix(path, constants.APIV1OrderPath):
		targetPath = p.stripAPIPrefix(path, constants.APIV1OrderPath)
	case strings.HasPrefix(path, constants.APIV1PortfolioPath):
		targetPath = p.stripAPIPrefix(path, constants.APIV1PortfolioPath)
	case strings.HasPrefix(path, constants.APIV1AssetPath):
		targetPath = p.stripAPIPrefix(path, constants.APIV1AssetPath)
	default:
		targetPath = path
	}

	proxyReq := &models.ProxyRequest{
		Method:        method,
		Path:          path,
		Headers:       headers,
		Body:          body,
		TargetService: constants.OrderService,
		TargetPath:    targetPath,
		Context: &models.RequestContext{
			RequestID:   generateRequestID(),
			Timestamp:   time.Now(),
			ServiceName: constants.OrderService,
		},
	}

	return p.ProxyRequest(ctx, proxyReq)
}

// stripAPIPrefix removes the API prefix from the path
// e.g., "/api/v1/auth/login" -> "/login"
func (p *ProxyService) stripAPIPrefix(path, prefix string) string {
	if strings.HasPrefix(path, prefix) {
		return strings.TrimPrefix(path, prefix)
	}
	return path
}

// generateRequestID generates a simple request ID
// Phase 2: Use UUID v4 for better uniqueness
func generateRequestID() string {
	return fmt.Sprintf("req-%d", time.Now().UnixNano())
}

// GetRouteConfig returns the route configuration for a given path
func (p *ProxyService) GetRouteConfig(path string) (*constants.RouteConfig, bool) {
	fmt.Printf("🔍 STEP 3: GetRouteConfig - Looking up path: %s\n", path)
	config, exists := constants.RouteConfigs[path]
	if !exists {
		fmt.Printf("🔍 STEP 3.1: GetRouteConfig - Route config not found for path: %s\n", path)
		fmt.Printf("🔍 STEP 3.2: GetRouteConfig - Available routes: %v\n", constants.RouteConfigs)
		return nil, false
	}
	fmt.Printf("🔍 STEP 3.3: GetRouteConfig - Route config found for path: %s\n", path)
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
		return constants.OrderService // Portfolio is handled by order service
	case strings.HasPrefix(path, constants.APIV1BalancePath):
		return constants.UserService // Balance is handled by user service
	case strings.HasPrefix(path, constants.APIV1AssetPath):
		return constants.OrderService // Asset balances handled by order service
	default:
		return ""
	}
}

// Phase 2: Circuit breaker pattern for service health monitoring (TODO)
// CircuitBreaker tracks service health and prevents cascading failures
// - Add failure count tracking
// - Add timeout tracking
// - Add state management (open, closed, half-open)
// - Add failure threshold configuration

// Phase 3: Advanced features (Future - simple comments)
// - Service discovery integration
// - Load balancing
// - Advanced monitoring and metrics
// - Retry logic with exponential backoff
// - Advanced caching strategies
