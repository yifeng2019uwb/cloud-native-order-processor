package config

import (
	"os"
	"strconv"
	"testing"

	"order-processor-gateway/pkg/constants"
)

func TestLoad(t *testing.T) {
	t.Run("Default Configuration", func(t *testing.T) {
		// Reset environment to defaults
		os.Unsetenv(constants.EnvGatewayPort)
		os.Unsetenv(constants.EnvGatewayHost)
		os.Unsetenv(constants.EnvRedisHost)
		os.Unsetenv(constants.EnvRedisPort)
		os.Unsetenv(constants.EnvRedisDB)
		os.Unsetenv(constants.EnvRedisSSL)
		os.Unsetenv(constants.EnvUserServiceURL)
		os.Unsetenv(constants.EnvInventoryServiceURL)

		cfg, err := Load()
		if err != nil {
			t.Fatalf("Expected Load to succeed, got error: %v", err)
		}

		// Verify server configuration
		if cfg.Server.Port != strconv.Itoa(constants.DefaultPort) {
			t.Errorf("Expected server port %d, got %s", constants.DefaultPort, cfg.Server.Port)
		}
		if cfg.Server.Host != constants.DefaultHost {
			t.Errorf("Expected server host %s, got %s", constants.DefaultHost, cfg.Server.Host)
		}

		// Verify Redis configuration
		if cfg.Redis.Host != constants.DefaultRedisHost {
			t.Errorf("Expected Redis host %s, got %s", constants.DefaultRedisHost, cfg.Redis.Host)
		}
		if cfg.Redis.Port != strconv.Itoa(constants.DefaultRedisPort) {
			t.Errorf("Expected Redis port %d, got %s", constants.DefaultRedisPort, cfg.Redis.Port)
		}
		if cfg.Redis.DB != constants.DefaultRedisDB {
			t.Errorf("Expected Redis DB %d, got %d", constants.DefaultRedisDB, cfg.Redis.DB)
		}
		if cfg.Redis.SSL != constants.DefaultRedisSSL {
			t.Errorf("Expected Redis SSL %t, got %t", constants.DefaultRedisSSL, cfg.Redis.SSL)
		}

		// Verify services configuration
		if cfg.Services.UserService != constants.DefaultUserServiceURL {
			t.Errorf("Expected user service URL %s, got %s", constants.DefaultUserServiceURL, cfg.Services.UserService)
		}
		if cfg.Services.InventoryService != constants.DefaultInventoryServiceURL {
			t.Errorf("Expected inventory service URL %s, got %s", constants.DefaultInventoryServiceURL, cfg.Services.InventoryService)
		}
	})

	t.Run("Custom Configuration", func(t *testing.T) {
		// Set custom environment variables
		customVars := map[string]string{
			constants.EnvGatewayPort:         "9090",
			constants.EnvGatewayHost:         "127.0.0.1",
			constants.EnvRedisHost:           "redis.example.com",
			constants.EnvRedisPort:           "6380",
			constants.EnvRedisPassword:       "secret",
			constants.EnvRedisDB:             "1",
			constants.EnvRedisSSL:            "true",
			constants.EnvUserServiceURL:      "http://custom-user:9000",
			constants.EnvInventoryServiceURL: "http://custom-inventory:9001",
		}

		// Set environment variables
		for key, value := range customVars {
			os.Setenv(key, value)
			defer os.Unsetenv(key)
		}

		cfg, err := Load()
		if err != nil {
			t.Fatalf("Expected Load to succeed, got error: %v", err)
		}

		// Verify custom values are applied
		if cfg.Server.Port != "9090" {
			t.Errorf("Expected port 9090, got %s", cfg.Server.Port)
		}
		if cfg.Server.Host != "127.0.0.1" {
			t.Errorf("Expected host 127.0.0.1, got %s", cfg.Server.Host)
		}
		if cfg.Redis.Host != "redis.example.com" {
			t.Errorf("Expected Redis host redis.example.com, got %s", cfg.Redis.Host)
		}
		if cfg.Redis.Port != "6380" {
			t.Errorf("Expected Redis port 6380, got %s", cfg.Redis.Port)
		}
		if cfg.Redis.Password != "secret" {
			t.Errorf("Expected Redis password secret, got %s", cfg.Redis.Password)
		}
		if cfg.Redis.DB != 1 {
			t.Errorf("Expected Redis DB 1, got %d", cfg.Redis.DB)
		}
		if !cfg.Redis.SSL {
			t.Errorf("Expected Redis SSL true, got %t", cfg.Redis.SSL)
		}
		if cfg.Services.UserService != "http://custom-user:9000" {
			t.Errorf("Expected user service URL http://custom-user:9000, got %s", cfg.Services.UserService)
		}
		if cfg.Services.InventoryService != "http://custom-inventory:9001" {
			t.Errorf("Expected inventory service URL http://custom-inventory:9001, got %s", cfg.Services.InventoryService)
		}
	})
}

func TestLoadWithInvalidRedisDB(t *testing.T) {
	// Set invalid Redis DB
	os.Setenv(constants.EnvRedisDB, "invalid")
	defer os.Unsetenv(constants.EnvRedisDB)

	_, err := Load()
	if err == nil {
		t.Error("Expected Load to fail with invalid Redis DB, but it succeeded")
	}
	if err.Error() != "invalid Redis DB configuration: strconv.Atoi: parsing \"invalid\": invalid syntax" {
		t.Errorf("Expected specific error message, got: %v", err)
	}
}

func TestLoadWithInvalidRedisSSL(t *testing.T) {
	// Set invalid Redis SSL
	os.Setenv(constants.EnvRedisSSL, "invalid")
	defer os.Unsetenv(constants.EnvRedisSSL)

	_, err := Load()
	if err == nil {
		t.Error("Expected Load to fail with invalid Redis SSL, but it succeeded")
	}
	if err.Error() != "invalid Redis SSL configuration: strconv.ParseBool: parsing \"invalid\": invalid syntax" {
		t.Errorf("Expected specific error message, got: %v", err)
	}
}

func TestGetEnv(t *testing.T) {
	t.Run("Environment Variable Set", func(t *testing.T) {
		key := constants.EnvRedisDB
		expectedValue := "test_value"
		fallback := "fallback_value"

		os.Setenv(key, expectedValue)
		defer os.Unsetenv(key)

		result := getEnv(key, fallback)
		if result != expectedValue {
			t.Errorf("Expected %s, got %s", expectedValue, result)
		}
	})

	t.Run("Environment Variable Not Set", func(t *testing.T) {
		key := "NONEXISTENT_ENV_VAR"
		fallback := "fallback_value"

		result := getEnv(key, fallback)
		if result != fallback {
			t.Errorf("Expected %s, got %s", fallback, result)
		}
	})

	t.Run("Environment Variable Empty", func(t *testing.T) {
		key := "EMPTY_ENV_VAR"
		fallback := "fallback_value"

		os.Setenv(key, "")
		defer os.Unsetenv(key)

		result := getEnv(key, fallback)
		if result != fallback {
			t.Errorf("Expected %s, got %s", fallback, result)
		}
	})
}

func TestConfigStructs(t *testing.T) {
	t.Run("ServerConfig", func(t *testing.T) {
		config := ServerConfig{
			Port: "8080",
			Host: "localhost",
		}

		if config.Port != "8080" {
			t.Errorf("Expected port 8080, got %s", config.Port)
		}
		if config.Host != "localhost" {
			t.Errorf("Expected host localhost, got %s", config.Host)
		}
	})

	t.Run("RedisConfig", func(t *testing.T) {
		config := RedisConfig{
			Host:     "redis.example.com",
			Port:     "6379",
			Password: "secret",
			DB:       0,
			SSL:      false,
		}

		if config.Host != "redis.example.com" {
			t.Errorf("Expected host redis.example.com, got %s", config.Host)
		}
		if config.Port != "6379" {
			t.Errorf("Expected port 6379, got %s", config.Port)
		}
		if config.Password != "secret" {
			t.Errorf("Expected password secret, got %s", config.Password)
		}
		if config.DB != 0 {
			t.Errorf("Expected DB 0, got %d", config.DB)
		}
		if config.SSL {
			t.Errorf("Expected SSL false, got %t", config.SSL)
		}
	})

	t.Run("ServicesConfig", func(t *testing.T) {
		config := ServicesConfig{
			UserService:      "http://user-service:8000",
			InventoryService: "http://inventory-service:8001",
		}

		if config.UserService != "http://user-service:8000" {
			t.Errorf("Expected user service http://user-service:8000, got %s", config.UserService)
		}
		if config.InventoryService != "http://inventory-service:8001" {
			t.Errorf("Expected inventory service http://inventory-service:8001, got %s", config.InventoryService)
		}
	})
}

func BenchmarkLoad(b *testing.B) {
	for i := 0; i < b.N; i++ {
		// Reset environment to defaults
		os.Unsetenv(constants.EnvGatewayPort)
		os.Unsetenv(constants.EnvGatewayHost)
		os.Unsetenv(constants.EnvRedisHost)
		os.Unsetenv(constants.EnvRedisPort)
		os.Unsetenv(constants.EnvRedisDB)
		os.Unsetenv(constants.EnvRedisSSL)
		os.Unsetenv(constants.EnvUserServiceURL)
		os.Unsetenv(constants.EnvInventoryServiceURL)

		_, err := Load()
		if err != nil {
			b.Fatalf("Load failed: %v", err)
		}
	}
}
