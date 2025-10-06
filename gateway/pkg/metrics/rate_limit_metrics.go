package metrics

import (
	"order-processor-gateway/pkg/constants"

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
				Name: constants.MetricRequestsTotal,
				Help: "Total number of requests processed by the gateway",
			},
			[]string{constants.LabelMethod, constants.LabelEndpoint, constants.LabelStatus, constants.LabelClientIP},
		),

		RateLimitViolationsTotal: factory.NewCounterVec(
			prometheus.CounterOpts{
				Name: constants.MetricRateLimitViolationsTotal,
				Help: "Total number of requests blocked by rate limiting",
			},
			[]string{constants.LabelClientIP, constants.LabelEndpoint},
		),

		RateLimitRemaining: factory.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: constants.MetricRateLimitRemaining,
				Help: "Number of requests remaining in current rate limit window",
			},
			[]string{constants.LabelClientIP, constants.LabelEndpoint},
		),

		RateLimitReset: factory.NewGaugeVec(
			prometheus.GaugeOpts{
				Name: constants.MetricRateLimitReset,
				Help: "Unix timestamp when the rate limit window resets",
			},
			[]string{constants.LabelClientIP, constants.LabelEndpoint},
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
