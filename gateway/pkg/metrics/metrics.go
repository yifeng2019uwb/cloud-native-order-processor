package metrics

import (
	"order-processor-gateway/pkg/constants"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

// GatewayMetrics holds the 4 gateway metrics: requests, errors, proxy_errors, latency.
type GatewayMetrics struct {
	RequestsTotal    *prometheus.CounterVec
	ErrorsTotal      *prometheus.CounterVec
	ProxyErrorsTotal *prometheus.CounterVec
	RequestLatency   *prometheus.HistogramVec
}

// NewGatewayMetrics creates and registers gateway metrics.
func NewGatewayMetrics() *GatewayMetrics {
	return NewGatewayMetricsWithRegistry(nil)
}

// NewGatewayMetricsWithRegistry creates and registers with a custom registry.
func NewGatewayMetricsWithRegistry(reg prometheus.Registerer) *GatewayMetrics {
	var factory promauto.Factory
	if reg != nil {
		factory = promauto.With(reg)
	} else {
		factory = promauto.With(prometheus.DefaultRegisterer)
	}
	return &GatewayMetrics{
		RequestsTotal: factory.NewCounterVec(
			prometheus.CounterOpts{
				Name: constants.MetricGatewayRequestsTotal,
				Help: "Total requests. Use rate(gateway_requests_total[5m]) for requests per 5 minutes. Labels: status_code, endpoint.",
			},
			[]string{constants.LabelStatusCode, constants.LabelEndpoint},
		),
		ErrorsTotal: factory.NewCounterVec(
			prometheus.CounterOpts{
				Name: constants.MetricGatewayErrorsTotal,
				Help: "Total 4xx+5xx responses. Use rate(gateway_errors_total[5m]) for error rate. Labels: status_code, endpoint.",
			},
			[]string{constants.LabelStatusCode, constants.LabelEndpoint},
		),
		ProxyErrorsTotal: factory.NewCounterVec(
			prometheus.CounterOpts{
				Name: constants.MetricProxyErrorsTotal,
				Help: "Proxy/backend failures (request_failed or backend 5xx). Labels: target_service, error_type. Use rate() for error rate.",
			},
			[]string{constants.LabelTargetService, constants.LabelErrorType},
		),
		RequestLatency: factory.NewHistogramVec(
			prometheus.HistogramOpts{
				Name:    constants.MetricGatewayRequestLatency,
				Help:    "Request latency in seconds. Use histogram_quantile(0.95, rate(gateway_request_latency_seconds_bucket[5m])) for p95. Label: endpoint.",
				Buckets: prometheus.DefBuckets,
			},
			[]string{constants.LabelEndpoint},
		),
	}
}

// RecordProxyError records a proxy/backend error (request_failed or 500, 502, 503).
func (m *GatewayMetrics) RecordProxyError(targetService, errorType string) {
	m.ProxyErrorsTotal.WithLabelValues(targetService, errorType).Inc()
}

// RecordRequest records one request (rate, errors if 4xx/5xx, latency).
func (m *GatewayMetrics) RecordRequest(endpoint, statusCode string, duration float64) {
	m.RequestsTotal.WithLabelValues(statusCode, endpoint).Inc()
	if len(statusCode) >= 1 && (statusCode[0] == '4' || statusCode[0] == '5') {
		m.ErrorsTotal.WithLabelValues(statusCode, endpoint).Inc()
	}
	m.RequestLatency.WithLabelValues(endpoint).Observe(duration)
}
