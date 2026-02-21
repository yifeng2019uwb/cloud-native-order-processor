package metrics

import (
	"testing"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/stretchr/testify/assert"
)

func TestNewGatewayMetrics(t *testing.T) {
	t.Run("Create with default registry", func(t *testing.T) {
		m := NewGatewayMetrics()
		assert.NotNil(t, m)
		assert.NotNil(t, m.RequestsTotal)
		assert.NotNil(t, m.ErrorsTotal)
		assert.NotNil(t, m.ProxyErrorsTotal)
		assert.NotNil(t, m.RequestLatency)
	})

	t.Run("Create with custom registry", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		m := NewGatewayMetricsWithRegistry(reg)
		assert.NotNil(t, m)
		assert.NotNil(t, m.RequestsTotal)
		assert.NotNil(t, m.ErrorsTotal)
		assert.NotNil(t, m.ProxyErrorsTotal)
		assert.NotNil(t, m.RequestLatency)
		err := reg.Register(m.RequestsTotal)
		assert.Error(t, err)
	})
}

func TestGatewayMetrics_RecordRequest(t *testing.T) {
	reg := prometheus.NewRegistry()
	m := NewGatewayMetricsWithRegistry(reg)

	t.Run("Record single request", func(t *testing.T) {
		m.RecordRequest("/api/v1/health", "200", 0.1)
		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record multiple requests and errors", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		m := NewGatewayMetricsWithRegistry(reg)
		m.RecordRequest("/api/v1/health", "200", 0.1)
		m.RecordRequest("/api/v1/auth/login", "200", 0.2)
		m.RecordRequest("/api/v1/orders", "401", 0.05)
		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})

	t.Run("Record various status codes", func(t *testing.T) {
		reg := prometheus.NewRegistry()
		m := NewGatewayMetricsWithRegistry(reg)
		for _, status := range []string{"200", "201", "400", "401", "404", "500", "503"} {
			m.RecordRequest("/test", status, 0.1)
		}
		metricFamilies, err := reg.Gather()
		assert.NoError(t, err)
		assert.Greater(t, len(metricFamilies), 0)
	})
}

func TestGatewayMetrics_Integration(t *testing.T) {
	reg := prometheus.NewRegistry()
	m := NewGatewayMetricsWithRegistry(reg)
	m.RecordRequest("/api/v1/orders", "200", 0.15)
	m.RecordRequest("/api/v1/orders", "503", 0.05)
	m.RecordProxyError("order_service", "request_failed")
	metricFamilies, err := reg.Gather()
	assert.NoError(t, err)
	assert.Greater(t, len(metricFamilies), 0)
}
