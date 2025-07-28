package utils

import (
	"order-processor-gateway/pkg/constants"
	"testing"
)

func TestGetServiceRateLimit(t *testing.T) {
	// Test user service rate limit
	userLimit := GetServiceRateLimit(constants.UserService)
	if userLimit.Limit != constants.UserServiceRateLimit {
		t.Errorf("Expected user service limit to be %d, got %d", constants.UserServiceRateLimit, userLimit.Limit)
	}
	if userLimit.WindowSize != constants.RateLimitWindow {
		t.Errorf("Expected user service window to be %v, got %v", constants.RateLimitWindow, userLimit.WindowSize)
	}

	// Test inventory service rate limit
	inventoryLimit := GetServiceRateLimit(constants.InventoryService)
	if inventoryLimit.Limit != constants.InventoryServiceRateLimit {
		t.Errorf("Expected inventory service limit to be %d, got %d", constants.InventoryServiceRateLimit, inventoryLimit.Limit)
	}
	if inventoryLimit.WindowSize != constants.RateLimitWindow {
		t.Errorf("Expected inventory service window to be %v, got %v", constants.RateLimitWindow, inventoryLimit.WindowSize)
	}

	// Test unknown service (should return default)
	unknownLimit := GetServiceRateLimit("unknown_service")
	if unknownLimit.Limit != constants.DefaultRateLimit {
		t.Errorf("Expected unknown service limit to be %d, got %d", constants.DefaultRateLimit, unknownLimit.Limit)
	}
	if unknownLimit.WindowSize != constants.RateLimitWindow {
		t.Errorf("Expected unknown service window to be %v, got %v", constants.RateLimitWindow, unknownLimit.WindowSize)
	}
}
