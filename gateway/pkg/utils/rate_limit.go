package utils

import (
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/models"
)

// GetServiceRateLimit returns rate limit config for a service
func GetServiceRateLimit(serviceName string) models.RateLimitInfo {
	limits := map[string]models.RateLimitInfo{
		constants.UserService: {
			Limit:      constants.UserServiceRateLimit,
			WindowSize: constants.RateLimitWindow,
		},
		constants.InventoryService: {
			Limit:      constants.InventoryServiceRateLimit,
			WindowSize: constants.RateLimitWindow,
		},
	}

	if limit, exists := limits[serviceName]; exists {
		return limit
	}

	// Default rate limit
	return models.RateLimitInfo{
		Limit:      constants.DefaultRateLimit,
		WindowSize: constants.RateLimitWindow,
	}
}
