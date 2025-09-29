package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// RateLimitMetrics holds all rate limiting related metrics
type RateLimitMetrics struct {
	// Total requests processed
	RequestsTotal *prometheus.CounterVec

	// Rate limit violations (requests blocked)
	RateLimitViolationsTotal *prometheus.CounterVec

	// Rate limit remaining (requests allowed in current window)
	RateLimitRemaining *prometheus.GaugeVec

	// Rate limit reset time (when the window resets)
	RateLimitReset *prometheus.GaugeVec
}

// NewRateLimitMetrics creates and registers new rate limiting metrics
func NewRateLimitMetrics() *RateLimitMetrics {
	return NewRateLimitMetricsWithRegistry(nil)
}

// NewRateLimitMetricsWithRegistry creates and registers new rate limiting metrics with a custom registry
func NewRateLimitMetricsWithRegistry(reg prometheus.Registerer) *RateLimitMetrics {
	var factory promauto.Factory
	if reg != nil {
		factory = promauto.With(reg)
	} else {
		factory = promauto.With(prometheus.DefaultRegisterer)
	}

	return &RateLimitMetrics{
		RequestsTotal: factory.NewCounterVec(
			prometheus.CounterOpts{
				Name: "gateway_requests_total",
				Help: "Total number of requests processed by the gateway",
			},
			[]string{"method", "endpoint", "status", "client_ip"},
		),

		RateLimitViolationsTotal: factory.NewCounterVec(
			prometheus.CounterOpts{
				Name: "gateway_rate_limit_violations_total",
				Help: "Total number of requests blocked by rate limiting",
			},
			[]string{"client_ip", "endpoint"},
		),

		RateLimitRemaining: factory.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "gateway_rate_limit_remaining",
				Help: "Number of requests remaining in current rate limit window",
			},
			[]string{"client_ip", "endpoint"},
		),

		RateLimitReset: factory.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: "gateway_rate_limit_reset",
				Help: "Unix timestamp when the rate limit window resets",
			},
			[]string{"client_ip", "endpoint"},
		),
	}
}

// RecordRequest records a processed request
func (m *RateLimitMetrics) RecordRequest(method, endpoint, status, clientIP string) {
	m.RequestsTotal.WithLabelValues(method, endpoint, status, clientIP).Inc()
}

// RecordRateLimitViolation records a rate limit violation
func (m *RateLimitMetrics) RecordRateLimitViolation(clientIP, endpoint string) {
	m.RateLimitViolationsTotal.WithLabelValues(clientIP, endpoint).Inc()
}

// UpdateRateLimitRemaining updates the remaining requests in the window
func (m *RateLimitMetrics) UpdateRateLimitRemaining(clientIP, endpoint string, remaining int64) {
	m.RateLimitRemaining.WithLabelValues(clientIP, endpoint).Set(float64(remaining))
}

// UpdateRateLimitReset updates the rate limit reset timestamp
func (m *RateLimitMetrics) UpdateRateLimitReset(clientIP, endpoint string, resetTime int64) {
	m.RateLimitReset.WithLabelValues(clientIP, endpoint).Set(float64(resetTime))
}
