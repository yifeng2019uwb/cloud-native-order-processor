package metrics

import (
	"testing"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/stretchr/testify/assert"
)

func TestNewRateLimitMetrics(t *testing.T) {
	t.Run("Create with default registry", func(t *testing.T) {
		// Use custom registry to avoid conflicts with other tests
		reg := prometheus.NewRegistry()
		metrics := NewRateLimitMetricsWithRegistry(reg)

		assert.NotNil(t, metrics)
		assert.NotNil(t, metrics.RequestsTotal)
		assert.NotNil(t, metrics.RateLimitViolationsTotal)
		assert.NotNil(t, metrics.RateLimitRemaining)
	})

	t.Run("Create with custom registry", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewRateLimitMetricsWithRegistry(reg)

		assert.NotNil(t, metrics)
		assert.NotNil(t, metrics.RequestsTotal)
		assert.NotNil(t, metrics.RateLimitViolationsTotal)
		assert.NotNil(t, metrics.RateLimitRemaining)

		// Verify metrics are registered in custom registry
		err := reg.Register(metrics.RequestsTotal)
		assert.Error(t, err) // Should fail because already registered
	})
}

func TestRateLimitMetrics_RecordRequest(t *testing.T) {
	reg := prometheus.NewRegistry()
	metrics := NewRateLimitMetricsWithRegistry(reg)

	t.Run("Record single request", func(t *testing.T) {
		metrics.RecordRequest("GET", "/api/v1/health", "200", "127.0.0.1")

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record multiple requests from same IP", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewRateLimitMetricsWithRegistry(reg)

		for i := 0; i < 5; i++ {
			metrics.RecordRequest("GET", "/api/v1/health", "200", "127.0.0.1")
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record requests from different IPs", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewRateLimitMetricsWithRegistry(reg)

		ips := []string{"127.0.0.1", "192.168.1.1", "10.0.0.1"}
		for _, ip := range ips {
			metrics.RecordRequest("GET", "/api/v1/health", "200", ip)
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record requests to different endpoints", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewRateLimitMetricsWithRegistry(reg)

		endpoints := []string{"/api/v1/health", "/api/v1/orders", "/api/v1/auth/login"}
		for _, endpoint := range endpoints {
			metrics.RecordRequest("GET", endpoint, "200", "127.0.0.1")
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record requests with different status codes", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewRateLimitMetricsWithRegistry(reg)

		statusCodes := []string{"200", "429", "401", "500"}
		for _, status := range statusCodes {
			metrics.RecordRequest("GET", "/api/v1/health", status, "127.0.0.1")
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})
}

func TestRateLimitMetrics_RecordRateLimitViolation(t *testing.T) {
	reg := prometheus.NewRegistry()
	metrics := NewRateLimitMetricsWithRegistry(reg)

	t.Run("Record single violation", func(t *testing.T) {
		metrics.RecordRateLimitViolation("127.0.0.1", "/api/v1/orders")

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record multiple violations from same IP", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewRateLimitMetricsWithRegistry(reg)

		for i := 0; i < 10; i++ {
			metrics.RecordRateLimitViolation("127.0.0.1", "/api/v1/orders")
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record violations from different IPs", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewRateLimitMetricsWithRegistry(reg)

		ips := []string{"127.0.0.1", "192.168.1.1", "10.0.0.1"}
		for _, ip := range ips {
			metrics.RecordRateLimitViolation(ip, "/api/v1/orders")
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record violations for different endpoints", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewRateLimitMetricsWithRegistry(reg)

		endpoints := []string{"/api/v1/orders", "/api/v1/inventory/assets", "/api/v1/auth/profile"}
		for _, endpoint := range endpoints {
			metrics.RecordRateLimitViolation("127.0.0.1", endpoint)
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})
}

func TestRateLimitMetrics_UpdateRateLimitRemaining(t *testing.T) {
	reg := prometheus.NewRegistry()
	metrics := NewRateLimitMetricsWithRegistry(reg)

	t.Run("Update remaining count", func(t *testing.T) {
		metrics.UpdateRateLimitRemaining("127.0.0.1", "/api/v1/orders", 100)

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Update remaining to zero", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewRateLimitMetricsWithRegistry(reg)

		metrics.UpdateRateLimitRemaining("127.0.0.1", "/api/v1/orders", 0)

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Update remaining multiple times", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		metrics := NewRateLimitMetricsWithRegistry(reg)

		remainingValues := []int64{100, 50, 25, 10, 0}
		for _, remaining := range remainingValues {
			metrics.UpdateRateLimitRemaining("127.0.0.1", "/api/v1/orders", remaining)
		}

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})
}

func TestRateLimitMetrics_Integration(t *testing.T) {
	reg := prometheus.NewRegistry()
	metrics := NewRateLimitMetricsWithRegistry(reg)

	t.Run("Complete rate limit flow", func(t *testing.T) {
		clientIP := "127.0.0.1"
		endpoint := "/api/v1/orders"

		// Record initial requests
		for i := 0; i < 5; i++ {
			metrics.RecordRequest("GET", endpoint, "200", clientIP)
			metrics.UpdateRateLimitRemaining(clientIP, endpoint, int64(1000-i-1))
		}

		// Record violation when limit exceeded
		metrics.RecordRateLimitViolation(clientIP, endpoint)
		metrics.UpdateRateLimitRemaining(clientIP, endpoint, 0)

		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})
}
