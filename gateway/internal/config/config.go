package config

import (
	"fmt"
	"os"
	"strconv"

	"order-processor-gateway/pkg/constants"
)

// Config holds all configuration for the gateway
type Config struct {
	Server   ServerConfig
	Redis    RedisConfig
	Services ServicesConfig
	JWT      JWTConfig
}

// ServerConfig holds server-related configuration
type ServerConfig struct {
	Port string
	Host string
}

// RedisConfig holds Redis connection configuration
type RedisConfig struct {
	Host     string
	Port     string
	Password string
	DB       int
	SSL      bool
}

// ServicesConfig holds backend service URLs
type ServicesConfig struct {
	UserService      string
	InventoryService string
}

// JWTConfig holds JWT configuration
type JWTConfig struct {
	SecretKey string
	Algorithm string
}

// Load loads configuration from environment variables
func Load() (*Config, error) {
	// Parse Redis configuration with error handling
	redisDB, err := strconv.Atoi(getEnv(constants.EnvRedisDB, strconv.Itoa(constants.DefaultRedisDB)))
	if err != nil {
		return nil, fmt.Errorf("invalid Redis DB configuration: %w", err)
	}

	redisSSL, err := strconv.ParseBool(getEnv(constants.EnvRedisSSL, strconv.FormatBool(constants.DefaultRedisSSL)))
	if err != nil {
		return nil, fmt.Errorf("invalid Redis SSL configuration: %w", err)
	}

	return &Config{
		Server: ServerConfig{
			Port: getEnv(constants.EnvGatewayPort, strconv.Itoa(constants.DefaultPort)),
			Host: getEnv(constants.EnvGatewayHost, constants.DefaultHost),
		},
		Redis: RedisConfig{
			Host:     getEnv(constants.EnvRedisHost, constants.DefaultRedisHost),
			Port:     getEnv(constants.EnvRedisPort, strconv.Itoa(constants.DefaultRedisPort)),
			Password: getEnv(constants.EnvRedisPassword, ""),
			DB:       redisDB,
			SSL:      redisSSL,
		},
		Services: ServicesConfig{
			UserService:      getEnv(constants.EnvUserServiceURL, constants.DefaultUserServiceURL),
			InventoryService: getEnv(constants.EnvInventoryServiceURL, constants.DefaultInventoryServiceURL),
		},
		JWT: JWTConfig{
			SecretKey: getEnv(constants.EnvJWTSecretKey, constants.DefaultJWTSecretKey),
			Algorithm: getEnv(constants.EnvJWTAlgorithm, constants.DefaultJWTAlgorithm),
		},
	}, nil
}

// getEnv gets environment variable with fallback
func getEnv(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}
