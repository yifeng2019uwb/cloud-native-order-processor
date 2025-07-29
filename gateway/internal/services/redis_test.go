package services

import (
	"context"
	"encoding/json"
	"fmt"
	"testing"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/pkg/constants"

	"github.com/stretchr/testify/assert"
)

func TestNewRedisService(t *testing.T) {
	t.Run("Valid Configuration", func(t *testing.T) {
		cfg := &config.RedisConfig{
			Host:     "localhost",
			Port:     "6379",
			Password: "",
			DB:       0,
			SSL:      false,
		}

		// Note: This test will fail if Redis is not running locally
		// In a real test environment, you'd use a test Redis instance or mock
		service, err := NewRedisService(cfg)

		if err != nil {
			// If Redis is not available, test the error handling
			assert.Contains(t, err.Error(), constants.ErrorRedisConnectionFailed)
			return
		}

		assert.NotNil(t, service)
		assert.NotNil(t, service.client)
		defer service.Close()
	})

	t.Run("Invalid Host", func(t *testing.T) {
		cfg := &config.RedisConfig{
			Host:     "invalid-host",
			Port:     "6379",
			Password: "",
			DB:       0,
			SSL:      false,
		}

		service, err := NewRedisService(cfg)

		assert.Error(t, err)
		assert.Nil(t, service)
		assert.Contains(t, err.Error(), constants.ErrorRedisConnectionFailed)
	})
}

func TestStoreSession(t *testing.T) {
	// Skip if Redis is not available
	cfg := &config.RedisConfig{
		Host:     "localhost",
		Port:     "6379",
		Password: "",
		DB:       0,
		SSL:      false,
	}

	service, err := NewRedisService(cfg)
	if err != nil {
		t.Skip("Redis not available, skipping test")
	}
	defer service.Close()

	ctx := context.Background()
	sessionID := "test-session-123"
	sessionData := map[string]interface{}{
		"user_id":    "user123",
		"user_role":  "admin",
		"expires_at": time.Now().Add(time.Hour).Unix(),
	}
	ttl := time.Hour

	err = service.StoreSession(ctx, sessionID, sessionData, ttl)
	assert.NoError(t, err)
}

func TestGetSession(t *testing.T) {
	// Skip if Redis is not available
	cfg := &config.RedisConfig{
		Host:     "localhost",
		Port:     "6379",
		Password: "",
		DB:       0,
		SSL:      false,
	}

	service, err := NewRedisService(cfg)
	if err != nil {
		t.Skip("Redis not available, skipping test")
	}
	defer service.Close()

	ctx := context.Background()
	sessionID := "test-session-456"
	sessionData := map[string]interface{}{
		"user_id":    "user456",
		"user_role":  "user",
		"expires_at": time.Now().Add(time.Hour).Unix(),
	}
	ttl := time.Hour

	// Store session first
	err = service.StoreSession(ctx, sessionID, sessionData, ttl)
	assert.NoError(t, err)

	// Retrieve session
	retrievedData, err := service.GetSession(ctx, sessionID)
	assert.NoError(t, err)
	assert.NotNil(t, retrievedData)
	assert.Equal(t, sessionData["user_id"], retrievedData["user_id"])
	assert.Equal(t, sessionData["user_role"], retrievedData["user_role"])
}

func TestGetSessionNotFound(t *testing.T) {
	// Skip if Redis is not available
	cfg := &config.RedisConfig{
		Host:     "localhost",
		Port:     "6379",
		Password: "",
		DB:       0,
		SSL:      false,
	}

	service, err := NewRedisService(cfg)
	if err != nil {
		t.Skip("Redis not available, skipping test")
	}
	defer service.Close()

	ctx := context.Background()
	sessionID := "non-existent-session"

	_, err = service.GetSession(ctx, sessionID)
	assert.Error(t, err)
}

func TestCheckRateLimit(t *testing.T) {
	// Skip if Redis is not available
	cfg := &config.RedisConfig{
		Host:     "localhost",
		Port:     "6379",
		Password: "",
		DB:       0,
		SSL:      false,
	}

	service, err := NewRedisService(cfg)
	if err != nil {
		t.Skip("Redis not available, skipping test")
	}
	defer service.Close()

	ctx := context.Background()
	key := "rate_limit:test-ip"
	limit := 5
	window := time.Minute

	// Test first request (should be allowed)
	allowed, err := service.CheckRateLimit(ctx, key, limit, window)
	assert.NoError(t, err)
	assert.True(t, allowed)

	// Test multiple requests within limit
	for i := 0; i < limit-1; i++ {
		allowed, err := service.CheckRateLimit(ctx, key, limit, window)
		assert.NoError(t, err)
		assert.True(t, allowed)
	}

	// Test request that exceeds limit
	allowed, err = service.CheckRateLimit(ctx, key, limit, window)
	assert.NoError(t, err)
	assert.False(t, allowed)
}

func TestCacheResponse(t *testing.T) {
	// Skip if Redis is not available
	cfg := &config.RedisConfig{
		Host:     "localhost",
		Port:     "6379",
		Password: "",
		DB:       0,
		SSL:      false,
	}

	service, err := NewRedisService(cfg)
	if err != nil {
		t.Skip("Redis not available, skipping test")
	}
	defer service.Close()

	ctx := context.Background()
	key := "cache:test-response"
	cacheData := map[string]interface{}{
		"status":    "success",
		"data":      []string{"item1", "item2", "item3"},
		"count":     3,
		"cached_at": time.Now().Unix(),
	}
	ttl := time.Minute * 5

	err = service.CacheResponse(ctx, key, cacheData, ttl)
	assert.NoError(t, err)
}

func TestGetCachedResponse(t *testing.T) {
	// Skip if Redis is not available
	cfg := &config.RedisConfig{
		Host:     "localhost",
		Port:     "6379",
		Password: "",
		DB:       0,
		SSL:      false,
	}

	service, err := NewRedisService(cfg)
	if err != nil {
		t.Skip("Redis not available, skipping test")
	}
	defer service.Close()

	ctx := context.Background()
	key := "cache:test-response-2"
	cacheData := map[string]interface{}{
		"status": "success",
		"data":   []string{"item1", "item2"},
		"count":  2,
	}
	ttl := time.Minute * 5

	// Store cache first
	err = service.CacheResponse(ctx, key, cacheData, ttl)
	assert.NoError(t, err)

	// Retrieve cached response
	cachedBytes, err := service.GetCachedResponse(ctx, key)
	assert.NoError(t, err)
	assert.NotNil(t, cachedBytes)

	// Verify the cached data
	var retrievedData map[string]interface{}
	err = json.Unmarshal(cachedBytes, &retrievedData)
	assert.NoError(t, err)
	assert.Equal(t, cacheData["status"], retrievedData["status"])
	assert.Equal(t, cacheData["count"], retrievedData["count"])
}

func TestGetCachedResponseNotFound(t *testing.T) {
	// Skip if Redis is not available
	cfg := &config.RedisConfig{
		Host:     "localhost",
		Port:     "6379",
		Password: "",
		DB:       0,
		SSL:      false,
	}

	service, err := NewRedisService(cfg)
	if err != nil {
		t.Skip("Redis not available, skipping test")
	}
	defer service.Close()

	ctx := context.Background()
	key := "cache:non-existent"

	_, err = service.GetCachedResponse(ctx, key)
	assert.Error(t, err)
}

func TestRedisServiceWithDifferentConfigs(t *testing.T) {
	testCases := []struct {
		name     string
		host     string
		port     string
		password string
		db       int
		ssl      bool
	}{
		{
			name:     "Default Config",
			host:     "localhost",
			port:     "6379",
			password: "",
			db:       0,
			ssl:      false,
		},
		{
			name:     "Custom Port",
			host:     "localhost",
			port:     "6380",
			password: "",
			db:       0,
			ssl:      false,
		},
		{
			name:     "With Password",
			host:     "localhost",
			port:     "6379",
			password: "secret",
			db:       0,
			ssl:      false,
		},
		{
			name:     "Custom DB",
			host:     "localhost",
			port:     "6379",
			password: "",
			db:       1,
			ssl:      false,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			cfg := &config.RedisConfig{
				Host:     tc.host,
				Port:     tc.port,
				Password: tc.password,
				DB:       tc.db,
				SSL:      tc.ssl,
			}

			service, err := NewRedisService(cfg)

			// Most of these will fail without actual Redis instances
			// but we can test the configuration parsing
			if err != nil {
				assert.Contains(t, err.Error(), constants.ErrorRedisConnectionFailed)
			} else {
				assert.NotNil(t, service)
				defer service.Close()
			}
		})
	}
}

func BenchmarkStoreSession(b *testing.B) {
	cfg := &config.RedisConfig{
		Host:     "localhost",
		Port:     "6379",
		Password: "",
		DB:       0,
		SSL:      false,
	}

	service, err := NewRedisService(cfg)
	if err != nil {
		b.Skip("Redis not available, skipping benchmark")
	}
	defer service.Close()

	ctx := context.Background()
	sessionData := map[string]interface{}{
		"user_id":    "benchmark-user",
		"user_role":  "user",
		"expires_at": time.Now().Add(time.Hour).Unix(),
	}
	ttl := time.Hour

	for i := 0; i < b.N; i++ {
		sessionID := fmt.Sprintf("benchmark-session-%d", i)
		err := service.StoreSession(ctx, sessionID, sessionData, ttl)
		if err != nil {
			b.Fatalf("StoreSession failed: %v", err)
		}
	}
}

func BenchmarkCheckRateLimit(b *testing.B) {
	cfg := &config.RedisConfig{
		Host:     "localhost",
		Port:     "6379",
		Password: "",
		DB:       0,
		SSL:      false,
	}

	service, err := NewRedisService(cfg)
	if err != nil {
		b.Skip("Redis not available, skipping benchmark")
	}
	defer service.Close()

	ctx := context.Background()
	limit := 1000
	window := time.Minute

	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("benchmark-rate-limit-%d", i)
		_, err := service.CheckRateLimit(ctx, key, limit, window)
		if err != nil {
			b.Fatalf("CheckRateLimit failed: %v", err)
		}
	}
}
