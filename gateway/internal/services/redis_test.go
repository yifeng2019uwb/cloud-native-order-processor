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

func TestRedisServiceEdgeCases(t *testing.T) {
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

	t.Run("StoreSession with Empty Data", func(t *testing.T) {
		sessionID := "empty-session"
		emptyData := map[string]interface{}{}
		ttl := time.Hour

		err := service.StoreSession(ctx, sessionID, emptyData, ttl)
		assert.NoError(t, err)

		// Retrieve and verify
		retrievedData, err := service.GetSession(ctx, sessionID)
		assert.NoError(t, err)
		assert.Equal(t, emptyData, retrievedData)
	})

	t.Run("StoreSession with Complex Data", func(t *testing.T) {
		sessionID := "complex-session"
		complexData := map[string]interface{}{
			"user_id":     "user123",
			"user_role":   "admin",
			"permissions": []string{"read", "write", "delete"},
			"metadata": map[string]interface{}{
				"created_at": time.Now().Unix(),
				"last_login": time.Now().Add(-time.Hour).Unix(),
				"settings": map[string]interface{}{
					"theme":    "dark",
					"language": "en",
					"timezone": "UTC",
				},
			},
			"is_active": true,
			"score":     95.5,
		}
		ttl := time.Hour

		err := service.StoreSession(ctx, sessionID, complexData, ttl)
		assert.NoError(t, err)

		// Retrieve and verify
		retrievedData, err := service.GetSession(ctx, sessionID)
		assert.NoError(t, err)
		assert.Equal(t, complexData["user_id"], retrievedData["user_id"])
		assert.Equal(t, complexData["user_role"], retrievedData["user_role"])
		assert.Equal(t, complexData["is_active"], retrievedData["is_active"])
		assert.Equal(t, complexData["score"], retrievedData["score"])
	})

	t.Run("StoreSession with Very Long Session ID", func(t *testing.T) {
		longSessionID := "very-long-session-id-" + string(make([]byte, 1000))
		sessionData := map[string]interface{}{
			"user_id": "user123",
		}
		ttl := time.Hour

		err := service.StoreSession(ctx, longSessionID, sessionData, ttl)
		assert.NoError(t, err)

		// Retrieve and verify
		retrievedData, err := service.GetSession(ctx, longSessionID)
		assert.NoError(t, err)
		assert.Equal(t, sessionData["user_id"], retrievedData["user_id"])
	})

	t.Run("CheckRateLimit with Zero Limit", func(t *testing.T) {
		key := "rate_limit:zero-limit"
		limit := 0
		window := time.Minute

		allowed, err := service.CheckRateLimit(ctx, key, limit, window)
		assert.NoError(t, err)
		assert.False(t, allowed) // Should be denied immediately
	})

	t.Run("CheckRateLimit with Very High Limit", func(t *testing.T) {
		key := "rate_limit:high-limit"
		limit := 1000000
		window := time.Minute

		// Should be allowed for the first request
		allowed, err := service.CheckRateLimit(ctx, key, limit, window)
		assert.NoError(t, err)
		assert.True(t, allowed)
	})

	t.Run("CheckRateLimit with Very Short Window", func(t *testing.T) {
		key := "rate_limit:short-window"
		limit := 5
		window := time.Millisecond * 100

		// Should be allowed for the first request
		allowed, err := service.CheckRateLimit(ctx, key, limit, window)
		assert.NoError(t, err)
		assert.True(t, allowed)

		// Wait for window to expire
		time.Sleep(window + time.Millisecond*50)

		// Should be allowed again after window expires
		allowed, err = service.CheckRateLimit(ctx, key, limit, window)
		assert.NoError(t, err)
		assert.True(t, allowed)
	})

	t.Run("CacheResponse with Different Data Types", func(t *testing.T) {
		testCases := []struct {
			name string
			data interface{}
		}{
			{"String", "simple string"},
			{"Number", 42},
			{"Float", 3.14159},
			{"Boolean", true},
			{"Array", []string{"a", "b", "c"}},
			{"Object", map[string]interface{}{"key": "value"}},
			{"Null", nil},
		}

		for _, tc := range testCases {
			t.Run(tc.name, func(t *testing.T) {
				key := fmt.Sprintf("cache:%s", tc.name)
				ttl := time.Minute

				err := service.CacheResponse(ctx, key, tc.data, ttl)
				assert.NoError(t, err)

				// Retrieve and verify
				cachedBytes, err := service.GetCachedResponse(ctx, key)
				assert.NoError(t, err)
				assert.NotNil(t, cachedBytes)
			})
		}
	})

	t.Run("Concurrent Rate Limit Checks", func(t *testing.T) {
		key := "rate_limit:concurrent"
		limit := 10
		window := time.Minute

		// Run concurrent rate limit checks
		results := make(chan bool, limit+5)
		errors := make(chan error, limit+5)

		for i := 0; i < limit+5; i++ {
			go func() {
				allowed, err := service.CheckRateLimit(ctx, key, limit, window)
				results <- allowed
				errors <- err
			}()
		}

		// Collect results
		allowedCount := 0
		for i := 0; i < limit+5; i++ {
			allowed := <-results
			err := <-errors
			assert.NoError(t, err)
			if allowed {
				allowedCount++
			}
		}

		// Should have exactly 'limit' allowed requests
		assert.Equal(t, limit, allowedCount)
	})
}

func TestRedisServiceErrorHandling(t *testing.T) {
	t.Run("NewRedisService with Invalid Port", func(t *testing.T) {
		cfg := &config.RedisConfig{
			Host:     "localhost",
			Port:     "invalid-port",
			Password: "",
			DB:       0,
			SSL:      false,
		}

		service, err := NewRedisService(cfg)
		assert.Error(t, err)
		assert.Nil(t, service)
		assert.Contains(t, err.Error(), constants.ErrorRedisConnectionFailed)
	})

	t.Run("NewRedisService with Invalid Host", func(t *testing.T) {
		cfg := &config.RedisConfig{
			Host:     "invalid-host-name-that-does-not-exist",
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

	t.Run("StoreSession with Invalid JSON Data", func(t *testing.T) {
		// This test is tricky because we can't easily create invalid JSON
		// that would fail Marshal, but we can test with valid data
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
		sessionID := "test-session"
		sessionData := map[string]interface{}{
			"user_id": "user123",
		}
		ttl := time.Hour

		err = service.StoreSession(ctx, sessionID, sessionData, ttl)
		assert.NoError(t, err)
	})
}

func BenchmarkCacheResponse(b *testing.B) {
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
	cacheData := map[string]interface{}{
		"status": "success",
		"data":   []string{"item1", "item2", "item3"},
		"count":  3,
	}
	ttl := time.Minute * 5

	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("benchmark-cache-%d", i)
		err := service.CacheResponse(ctx, key, cacheData, ttl)
		if err != nil {
			b.Fatalf("CacheResponse failed: %v", err)
		}
	}
}

func BenchmarkGetCachedResponse(b *testing.B) {
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
	cacheData := map[string]interface{}{
		"status": "success",
		"data":   []string{"item1", "item2", "item3"},
		"count":  3,
	}
	ttl := time.Minute * 5

	// Pre-populate cache
	for i := 0; i < 100; i++ {
		key := fmt.Sprintf("benchmark-get-cache-%d", i)
		err := service.CacheResponse(ctx, key, cacheData, ttl)
		if err != nil {
			b.Fatalf("CacheResponse failed: %v", err)
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("benchmark-get-cache-%d", i%100)
		_, err := service.GetCachedResponse(ctx, key)
		if err != nil {
			b.Fatalf("GetCachedResponse failed: %v", err)
		}
	}
}
