package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// GatewayMetrics holds all gateway-related metrics
type GatewayMetrics struct {
	// HTTP request metrics
	HTTPRequestsTotal   *prometheus.CounterVec
	HTTPRequestDuration *prometheus.HistogramVec

	// Proxy service metrics
	ProxyRequestsTotal   *prometheus.CounterVec
	ProxyRequestDuration *prometheus.HistogramVec
	ProxyErrorsTotal     *prometheus.CounterVec

	// Rate limiting metrics
	RateLimit *RateLimitMetrics
}

// NewGatewayMetrics creates and registers all gateway metrics
func NewGatewayMetrics() *GatewayMetrics {
	return NewGatewayMetricsWithRegistry(nil)
}

// NewGatewayMetricsWithRegistry creates and registers all gateway metrics with a custom registry
func NewGatewayMetricsWithRegistry(reg prometheus.Registerer) *GatewayMetrics {
	var factory promauto.Factory
	if reg != nil {
		factory = promauto.With(reg)
	} else {
		factory = promauto.With(prometheus.DefaultRegisterer)
	}

	return &GatewayMetrics{
		HTTPRequestsTotal: factory.NewCounterVec(
			prometheus.CounterOpts{
				Name: "gateway_http_requests_total",
				Help: "Total number of HTTP requests processed",
			},
			[]string{"method", "path", "status_code", "service"},
		),

		HTTPRequestDuration: factory.NewHistogramVec(
			prometheus.HistogramOpts{
				Name:    "gateway_http_request_duration_seconds",
				Help:    "Duration of HTTP requests in seconds",
				Buckets: prometheus.DefBuckets,
			},
			[]string{"method", "path", "status_code", "service"},
		),

		ProxyRequestsTotal: factory.NewCounterVec(
			prometheus.CounterOpts{
				Name: "gateway_proxy_requests_total",
				Help: "Total number of proxy requests to backend services",
			},
			[]string{"target_service", "method", "status_code"},
		),

		ProxyRequestDuration: factory.NewHistogramVec(
			prometheus.HistogramOpts{
				Name:    "gateway_proxy_request_duration_seconds",
				Help:    "Duration of proxy requests to backend services in seconds",
				Buckets: prometheus.DefBuckets,
			},
			[]string{"target_service", "method", "status_code"},
		),

		ProxyErrorsTotal: factory.NewCounterVec(
			prometheus.CounterOpts{
				Name: "gateway_proxy_errors_total",
				Help: "Total number of proxy errors to backend services",
			},
			[]string{"target_service", "error_type"},
		),

		RateLimit: NewRateLimitMetricsWithRegistry(reg),
	}
}

// RecordHTTPRequest records an HTTP request
func (m *GatewayMetrics) RecordHTTPRequest(method, path, statusCode, service string, duration float64) {
	m.HTTPRequestsTotal.WithLabelValues(method, path, statusCode, service).Inc()
	m.HTTPRequestDuration.WithLabelValues(method, path, statusCode, service).Observe(duration)
}

// RecordProxyRequest records a proxy request
func (m *GatewayMetrics) RecordProxyRequest(targetService, method, statusCode string, duration float64) {
	m.ProxyRequestsTotal.WithLabelValues(targetService, method, statusCode).Inc()
	m.ProxyRequestDuration.WithLabelValues(targetService, method, statusCode).Observe(duration)
}

// RecordProxyError records a proxy error
func (m *GatewayMetrics) RecordProxyError(targetService, errorType string) {
	m.ProxyErrorsTotal.WithLabelValues(targetService, errorType).Inc()
}
