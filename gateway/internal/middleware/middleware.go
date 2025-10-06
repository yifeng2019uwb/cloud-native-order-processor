package middleware

import (
	"fmt"
	"time"

	"order-processor-gateway/pkg/constants"

	"github.com/gin-gonic/gin"
)

// CORS middleware for handling cross-origin requests
func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", constants.CORSAllowOrigin)
		c.Header("Access-Control-Allow-Methods", constants.CORSAllowMethods)
		c.Header("Access-Control-Allow-Headers", constants.CORSAllowHeaders)

		if c.Request.Method == constants.HTTPMethodOptions {
			c.AbortWithStatus(constants.StatusNoContent)
			return
		}

		c.Next()
	}
}

// Logger middleware for request logging
func Logger() gin.HandlerFunc {
	return gin.LoggerWithFormatter(func(param gin.LogFormatterParams) string {
		return fmt.Sprintf("%s - [%s] \"%s %s %s %d %s \"%s\" %s\"\n",
			param.ClientIP,
			param.TimeStamp.Format(time.RFC1123),
			param.Method,
			param.Path,
			param.Request.Proto,
			param.StatusCode,
			param.Latency,
			param.Request.UserAgent(),
			param.ErrorMessage,
		)
	})
}

// Recovery middleware for panic recovery
func Recovery() gin.HandlerFunc {
	return gin.Recovery()
}
