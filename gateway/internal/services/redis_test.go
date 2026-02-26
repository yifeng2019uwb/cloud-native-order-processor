package services

import (
	"context"
	"fmt"
	"strings"
	"testing"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/pkg/constants"

	"github.com/alicebob/miniredis/v2"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewRedisService(t *testing.T) {
	t.Run("Valid Configuration", func(t *testing.T) {
		service := newRedisServiceWithMiniredis(t)
		assert.NotNil(t, service)
		assert.NotNil(t, service.client)
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

func TestCheckRateLimit(t *testing.T) {
	service := newRedisServiceWithMiniredis(t)
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

func TestCheckRateLimitWithDetails(t *testing.T) {
	service := newRedisServiceWithMiniredis(t)
	ctx := context.Background()
	key := constants.RedisKeyPrefixRateLimit + fmt.Sprintf("details-%d", time.Now().UnixNano())
	limit := constants.FailedLoginBlockThreshold
	window := constants.RateLimitWindow

	allowed, remaining, resetTime, err := service.CheckRateLimitWithDetails(ctx, key, limit, window)
	assert.NoError(t, err)
	assert.True(t, allowed)
	assert.Equal(t, int64(limit-1), remaining)
	assert.Greater(t, resetTime, int64(0))

	// Exhaust limit
	for i := 0; i < limit; i++ {
		_, _, _, err = service.CheckRateLimitWithDetails(ctx, key, limit, window)
		assert.NoError(t, err)
	}
	allowed, remaining, _, err = service.CheckRateLimitWithDetails(ctx, key, limit, window)
	assert.NoError(t, err)
	assert.False(t, allowed)
	assert.Equal(t, int64(0), remaining)
}

// newRedisServiceWithMiniredis starts an in-memory Redis and returns a RedisService connected to it (no real Redis required).
func newRedisServiceWithMiniredis(t *testing.T) *RedisService {
	mr := miniredis.RunT(t)
	addr := mr.Addr()
	parts := strings.Split(addr, ":")
	require.Len(t, parts, 2, "miniredis addr should be host:port")
	cfg := &config.RedisConfig{Host: parts[0], Port: parts[1], Password: "", DB: 0, SSL: false}
	svc, err := NewRedisService(cfg)
	require.NoError(t, err)
	t.Cleanup(func() { _ = svc.Close() })
	return svc
}

func TestIsIPBlocked(t *testing.T) {
	service := newRedisServiceWithMiniredis(t)
	ctx := context.Background()
	testIP := fmt.Sprintf("test-blocked-ip-%d", time.Now().UnixNano())

	blocked, err := service.IsIPBlocked(ctx, testIP)
	assert.NoError(t, err)
	assert.False(t, blocked)

	err = service.SetIPBlock(ctx, testIP, 60*time.Second)
	assert.NoError(t, err)

	blocked, err = service.IsIPBlocked(ctx, testIP)
	assert.NoError(t, err)
	assert.True(t, blocked)

	blocked, err = service.IsIPBlocked(ctx, "192.0.2.99")
	assert.NoError(t, err)
	assert.False(t, blocked)
}

func TestRecordFailedLogin(t *testing.T) {
	service := newRedisServiceWithMiniredis(t)
	ctx := context.Background()
	testIP := fmt.Sprintf("test-fail-login-%d", time.Now().UnixNano())
	failKey := constants.RedisKeyPrefixLoginFail + testIP
	blockKey := constants.RedisKeyPrefixIPBlock + testIP
	defer func() {
		service.client.Del(ctx, failKey)
		service.client.Del(ctx, blockKey)
	}()

	for i := 0; i < constants.FailedLoginBlockThreshold; i++ {
		err := service.RecordFailedLogin(ctx, testIP)
		assert.NoError(t, err)
	}

	n, err := service.client.Exists(ctx, blockKey).Result()
	assert.NoError(t, err)
	assert.GreaterOrEqual(t, n, int64(1), "ip_block key should be set after threshold")

	_, err = service.client.Get(ctx, failKey).Result()
	assert.NoError(t, err)
}

func TestRedisServiceEdgeCases(t *testing.T) {
	service := newRedisServiceWithMiniredis(t)
	ctx := context.Background()

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
