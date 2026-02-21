package middleware

import (
	"strconv"
	"time"

	"order-processor-gateway/pkg/metrics"

	"github.com/gin-gonic/gin"
)

// MetricsHTTP records the 3 gateway metrics (requests, errors, latency) per request.
func MetricsHTTP(gm *metrics.GatewayMetrics) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()
		duration := time.Since(start).Seconds()
		statusCode := strconv.Itoa(c.Writer.Status())
		endpoint := c.Request.URL.Path
		gm.RecordRequest(endpoint, statusCode, duration)
	}
}
