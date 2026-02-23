package services

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/pkg/constants"

	"github.com/redis/go-redis/v9"
)

// RedisService handles Redis operations
type RedisService struct {
	client *redis.Client
}

// NewRedisService creates a new Redis service
func NewRedisService(cfg *config.RedisConfig) (*RedisService, error) {
	client := redis.NewClient(&redis.Options{
		Addr:     fmt.Sprintf("%s:%s", cfg.Host, cfg.Port),
		Password: cfg.Password,
		DB:       cfg.DB,
	})

	// Test connection
	ctx, cancel := context.WithTimeout(context.Background(), constants.RedisTimeout)
	defer cancel()

	if err := client.Ping(ctx).Err(); err != nil {
		return nil, fmt.Errorf("%s %w", constants.ErrorRedisConnectionFailed, err)
	}

	return &RedisService{client: client}, nil
}

// StoreSession stores user session data
func (r *RedisService) StoreSession(ctx context.Context, sessionID string, data map[string]interface{}, ttl time.Duration) error {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return err
	}

	return r.client.Set(ctx, constants.RedisKeyPrefixSession+sessionID, jsonData, ttl).Err()
}

// GetSession retrieves user session data
func (r *RedisService) GetSession(ctx context.Context, sessionID string) (map[string]interface{}, error) {
	key := constants.RedisKeyPrefixSession + sessionID
	data, err := r.client.Get(ctx, key).Result()
	if err != nil {
		return nil, err
	}

	var session map[string]interface{}
	if err := json.Unmarshal([]byte(data), &session); err != nil {
		return nil, err
	}

	return session, nil
}

// CheckRateLimit checks if request is within rate limits
func (r *RedisService) CheckRateLimit(ctx context.Context, key string, limit int, window time.Duration) (bool, error) {
	current, err := r.client.Incr(ctx, key).Result()
	if err != nil {
		return false, err
	}

	// Set expiry on first request
	if current == 1 {
		r.client.Expire(ctx, key, window)
	}

	return current <= int64(limit), nil
}

// CheckRateLimitWithDetails checks if request is within rate limits and returns additional details
func (r *RedisService) CheckRateLimitWithDetails(ctx context.Context, key string, limit int, window time.Duration) (bool, int64, int64, error) {
	// Get current count
	current, err := r.client.Incr(ctx, key).Result()
	if err != nil {
		return false, 0, 0, err
	}

	// Set expiry on first request
	if current == 1 {
		r.client.Expire(ctx, key, window)
	}

	// Calculate remaining requests
	remaining := int64(limit) - current
	if remaining < 0 {
		remaining = 0
	}

	// Get TTL to calculate reset time
	ttl, err := r.client.TTL(ctx, key).Result()
	if err != nil {
		return false, remaining, 0, err
	}

	// Calculate reset time (current time + TTL)
	resetTime := time.Now().Add(ttl).Unix()

	allowed := current <= int64(limit)
	return allowed, remaining, resetTime, nil
}

// CacheResponse caches API responses
func (r *RedisService) CacheResponse(ctx context.Context, key string, data interface{}, ttl time.Duration) error {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return err
	}

	return r.client.Set(ctx, key, jsonData, ttl).Err()
}

// GetCachedResponse retrieves cached response
func (r *RedisService) GetCachedResponse(ctx context.Context, key string) ([]byte, error) {
	return r.client.Get(ctx, key).Bytes()
}

// IsIPBlocked returns true if the client IP has an active block key (ip_block:<ip> with TTL).
// Ops: block with TTL via redis-cli SET ip_block:<ip> 1 EX <seconds> (e.g. EX 300 for 5 min dev/test, EX 86400 for 24hr production).
func (r *RedisService) IsIPBlocked(ctx context.Context, clientIP string) (bool, error) {
	key := constants.RedisKeyPrefixIPBlock + clientIP
	n, err := r.client.Exists(ctx, key).Result()
	if err != nil {
		return false, err
	}
	return n > 0, nil
}

// RecordFailedLogin increments the failed-login count for the client IP. If the count reaches FailedLoginBlockThreshold
// within the window (FailedLoginWindowSeconds), sets the IP block key (ip_block:<ip>) with TTL BlockDurationSeconds.
// Call this when the gateway receives 401 from POST /auth/login.
func (r *RedisService) RecordFailedLogin(ctx context.Context, clientIP string) error {
	keyFail := constants.RedisKeyPrefixLoginFail + clientIP
	count, err := r.client.Incr(ctx, keyFail).Result()
	if err != nil {
		return err
	}
	if count == 1 {
		r.client.Expire(ctx, keyFail, time.Duration(constants.FailedLoginWindowSeconds)*time.Second)
	}
	if count >= int64(constants.FailedLoginBlockThreshold) {
		blockKey := constants.RedisKeyPrefixIPBlock + clientIP
		if err := r.client.Set(ctx, blockKey, "1", time.Duration(constants.BlockDurationSeconds)*time.Second).Err(); err != nil {
			return err
		}
	}
	return nil
}

// Close closes Redis connection
func (r *RedisService) Close() error {
	return r.client.Close()
}
