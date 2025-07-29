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

// Close closes Redis connection
func (r *RedisService) Close() error {
	return r.client.Close()
}
