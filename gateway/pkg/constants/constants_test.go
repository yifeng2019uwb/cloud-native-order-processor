package constants

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestIPBlockConstants(t *testing.T) {
	assert.Greater(t, FailedLoginBlockThreshold, 0, "FailedLoginBlockThreshold must be positive")
	assert.Greater(t, BlockDurationSeconds, 0, "BlockDurationSeconds must be positive")
	assert.Greater(t, FailedLoginWindowSeconds, 0, "FailedLoginWindowSeconds must be positive")
	// Default: block and window TTL match so count expires with block
	assert.Equal(t, BlockDurationSeconds, FailedLoginWindowSeconds, "block and window TTL should match for default dev/test")
}

func TestRateLimitWindow(t *testing.T) {
	assert.True(t, RateLimitWindow > 0 && RateLimitWindow <= 24*time.Hour, "RateLimitWindow must be positive and at most 24h")
}

func TestRedisKeyPrefixes(t *testing.T) {
	assert.NotEmpty(t, RedisKeyPrefixIPBlock, "RedisKeyPrefixIPBlock must be set")
	assert.NotEmpty(t, RedisKeyPrefixLoginFail, "RedisKeyPrefixLoginFail must be set")
	assert.NotEqual(t, RedisKeyPrefixIPBlock, RedisKeyPrefixLoginFail, "IP block and login-fail prefixes must differ")
}
