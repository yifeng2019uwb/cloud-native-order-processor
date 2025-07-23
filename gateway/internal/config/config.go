package config

import (
	"os"
	"strconv"
)

// Config holds all configuration for the gateway
type Config struct {
	Server ServerConfig
	Redis  RedisConfig
	Services ServicesConfig
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
	UserService     string
	InventoryService string
}

// Load loads configuration from environment variables
func Load() (*Config, error) {
	redisDB, _ := strconv.Atoi(getEnv("REDIS_DB", "0"))
	redisSSL, _ := strconv.ParseBool(getEnv("REDIS_SSL", "false"))

	return &Config{
		Server: ServerConfig{
			Port: getEnv("GATEWAY_PORT", "8080"),
			Host: getEnv("GATEWAY_HOST", "0.0.0.0"),
		},
		Redis: RedisConfig{
			Host:     getEnv("REDIS_HOST", "localhost"),
			Port:     getEnv("REDIS_PORT", "6379"),
			Password: getEnv("REDIS_PASSWORD", ""),
			DB:       redisDB,
			SSL:      redisSSL,
		},
		Services: ServicesConfig{
			UserService:     getEnv("USER_SERVICE_URL", "http://user-service:8000"),
			InventoryService: getEnv("INVENTORY_SERVICE_URL", "http://inventory-service:8001"),
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