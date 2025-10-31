package metrics

import (
	"testing"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/stretchr/testify/assert"
)

func TestNewGatewayMetrics(t *testing.T) {
	t.Run("Create with default registry", func(t *testing.T) {
		metrics := NewGatewayMetrics()

		assert.NotNil(t, metrics)
		assert.NotNil(t, metrics.HTTPRequestsTotal)
		assert.NotNil(t, metrics.HTTPRequestDuration)
		assert.NotNil(t, metrics.ProxyRequestsTotal)
		assert.NotNil(t, metrics.ProxyRequestDuration)
		assert.NotNil(t, metrics.ProxyErrorsTotal)
		assert.NotNil(t, metrics.RateLimit)
	})

	t.Run("Create with custom registry", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewGatewayMetricsWithRegistry(reg)

		assert.NotNil(t, metrics)
		assert.NotNil(t, metrics.HTTPRequestsTotal)
		assert.NotNil(t, metrics.HTTPRequestDuration)
		assert.NotNil(t, metrics.ProxyRequestsTotal)
		assert.NotNil(t, metrics.ProxyRequestDuration)
		assert.NotNil(t, metrics.ProxyErrorsTotal)
		assert.NotNil(t, metrics.RateLimit)

		// Verify metrics are registered in custom registry
		err := reg.Register(metrics.HTTPRequestsTotal)
		assert.Error(t, err) // Should fail because already registered
	})
}

func TestGatewayMetrics_RecordHTTPRequest(t *testing.T) {
	reg := prometheus.NewRegistry()
	metrics := NewGatewayMetricsWithRegistry(reg)

	t.Run("Record single request", func(t *testing.T) {
		metrics.RecordHTTPRequest("GET", "/api/v1/health", "200", "gateway", 0.1)

		// Collect metrics
		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record multiple requests", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewGatewayMetricsWithRegistry(reg)

		metrics.RecordHTTPRequest("GET", "/api/v1/health", "200", "gateway", 0.1)
		metrics.RecordHTTPRequest("POST", "/api/v1/auth/login", "200", "gateway", 0.2)
		metrics.RecordHTTPRequest("GET", "/api/v1/orders", "401", "gateway", 0.05)

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record request with different status codes", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewGatewayMetricsWithRegistry(reg)

		statusCodes := []string{"200", "201", "400", "401", "404", "500", "503"}
		for _, status := range statusCodes {
			metrics.RecordHTTPRequest("GET", "/test", status, "gateway", 0.1)
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})
}

func TestGatewayMetrics_RecordProxyRequest(t *testing.T) {
	reg := prometheus.NewRegistry()
	metrics := NewGatewayMetricsWithRegistry(reg)

	t.Run("Record proxy request", func(t *testing.T) {
		metrics.RecordProxyRequest("user_service", "GET", "200", 0.15)

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record proxy requests to different services", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewGatewayMetricsWithRegistry(reg)

		services := []string{"user_service", "inventory_service", "order_service", "auth_service"}
		for _, service := range services {
			metrics.RecordProxyRequest(service, "GET", "200", 0.1)
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record proxy request with error status", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewGatewayMetricsWithRegistry(reg)

		metrics.RecordProxyRequest("user_service", "GET", "500", 0.05)

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})
}

func TestGatewayMetrics_RecordProxyError(t *testing.T) {
	reg := prometheus.NewRegistry()
	metrics := NewGatewayMetricsWithRegistry(reg)

	t.Run("Record proxy error", func(t *testing.T) {
		metrics.RecordProxyError("user_service", "connection_timeout")

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record different error types", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewGatewayMetricsWithRegistry(reg)

		errorTypes := []string{"connection_timeout", "circuit_breaker_open", "service_unavailable", "network_error"}
		for _, errorType := range errorTypes {
			metrics.RecordProxyError("user_service", errorType)
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record errors for different services", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewGatewayMetricsWithRegistry(reg)

		services := []string{"user_service", "inventory_service", "order_service"}
		for _, service := range services {
			metrics.RecordProxyError(service, "timeout")
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})
}

func TestGatewayMetrics_Integration(t *testing.T) {
	reg := prometheus.NewRegistry()
	metrics := NewGatewayMetricsWithRegistry(reg)

	t.Run("Complete request flow", func(t *testing.T) {
		// Simulate a complete request flow
		metrics.RecordHTTPRequest("GET", "/api/v1/orders", "200", "gateway", 0.15)
		metrics.RecordProxyRequest("order_service", "GET", "200", 0.12)

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Error flow", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewGatewayMetricsWithRegistry(reg)

		metrics.RecordHTTPRequest("GET", "/api/v1/orders", "503", "gateway", 0.05)
		metrics.RecordProxyError("order_service", "service_unavailable")

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})
}
