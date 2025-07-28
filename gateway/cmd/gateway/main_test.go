package main

import (
	"os"
	"strconv"
	"testing"

	"order-processor-gateway/internal/config"
	"order-processor-gateway/pkg/constants"
)

// TestMainConstants tests that all constants used in main.go are properly defined
func TestMainConstants(t *testing.T) {
	// Test application constants
	if constants.AppName == "" {
		t.Error("AppName constant should not be empty")
	}
	if constants.AppVersion == "" {
		t.Error("AppVersion constant should not be empty")
	}

	// Test log message constants
	requiredLogConstants := []string{
		constants.LogConfigLoadFailed,
		constants.LogRedisConnectFailed,
		constants.LogRedisConnectSuccess,
		constants.LogRedisContinueWithout,
		constants.LogProxyInitSuccess,
		constants.LogServerStart,
		constants.LogServerStartFailed,
	}

	for _, constant := range requiredLogConstants {
		if constant == "" {
			t.Errorf("Log constant should not be empty: %s", constant)
		}
	}
}

// TestMainConfigurationLoading tests the configuration loading logic used in main.go
func TestMainConfigurationLoading(t *testing.T) {
	t.Run("Default Configuration", func(t *testing.T) {
		// Reset environment to defaults
		os.Unsetenv(constants.EnvGatewayPort)
		os.Unsetenv(constants.EnvGatewayHost)
		os.Unsetenv(constants.EnvRedisHost)
		os.Unsetenv(constants.EnvRedisPort)

		// Test configuration loading (this is what main() does)
		cfg, err := config.Load()
		if err != nil {
			t.Fatalf("Expected configuration to load successfully, got error: %v", err)
		}

		// Verify essential configuration is loaded
		if cfg.Server.Port == "" {
			t.Error("Expected server port to be set")
		}
		if cfg.Server.Host == "" {
			t.Error("Expected server host to be set")
		}
		if cfg.Services.UserService == "" {
			t.Error("Expected user service URL to be set")
		}
		if cfg.Services.InventoryService == "" {
			t.Error("Expected inventory service URL to be set")
		}
	})

	t.Run("Custom Configuration", func(t *testing.T) {
		// Set custom environment variables
		customVars := map[string]string{
			constants.EnvGatewayPort:         "9090",
			constants.EnvGatewayHost:         "127.0.0.1",
			constants.EnvRedisHost:           "redis.example.com",
			constants.EnvRedisPort:           "6380",
			constants.EnvUserServiceURL:      "http://custom-user:9000",
			constants.EnvInventoryServiceURL: "http://custom-inventory:9001",
		}

		// Set environment variables
		for key, value := range customVars {
			os.Setenv(key, value)
			defer os.Unsetenv(key)
		}

		// Test configuration loading
		cfg, err := config.Load()
		if err != nil {
			t.Fatalf("Expected configuration to load successfully, got error: %v", err)
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
		if cfg.Services.UserService != "http://custom-user:9000" {
			t.Errorf("Expected user service URL http://custom-user:9000, got %s", cfg.Services.UserService)
		}
		if cfg.Services.InventoryService != "http://custom-inventory:9001" {
			t.Errorf("Expected inventory service URL http://custom-inventory:9001, got %s", cfg.Services.InventoryService)
		}
	})
}

// TestMainServiceURLs tests the service URL configuration logic
func TestMainServiceURLs(t *testing.T) {
	tests := []struct {
		name     string
		envVar   string
		envValue string
		expected string
	}{
		{
			name:     "Default User Service URL",
			envVar:   constants.EnvUserServiceURL,
			envValue: "",
			expected: constants.DefaultUserServiceURL,
		},
		{
			name:     "Custom User Service URL",
			envVar:   constants.EnvUserServiceURL,
			envValue: "http://custom-user-service:9000",
			expected: "http://custom-user-service:9000",
		},
		{
			name:     "Default Inventory Service URL",
			envVar:   constants.EnvInventoryServiceURL,
			envValue: "",
			expected: constants.DefaultInventoryServiceURL,
		},
		{
			name:     "Custom Inventory Service URL",
			envVar:   constants.EnvInventoryServiceURL,
			envValue: "http://custom-inventory-service:9001",
			expected: "http://custom-inventory-service:9001",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Set environment variable
			if tt.envValue != "" {
				os.Setenv(tt.envVar, tt.envValue)
				defer os.Unsetenv(tt.envVar)
			}

			// Load configuration
			cfg, err := config.Load()
			if err != nil {
				t.Fatalf("Failed to load configuration: %v", err)
			}

			// Check service URL
			var actualURL string
			switch tt.envVar {
			case constants.EnvUserServiceURL:
				actualURL = cfg.Services.UserService
			case constants.EnvInventoryServiceURL:
				actualURL = cfg.Services.InventoryService
			}

			if actualURL != tt.expected {
				t.Errorf("Expected URL %s, got %s", tt.expected, actualURL)
			}
		})
	}
}

// TestMainRedisConfiguration tests Redis configuration loading
func TestMainRedisConfiguration(t *testing.T) {
	tests := []struct {
		name     string
		envVars  map[string]string
		expected config.RedisConfig
	}{
		{
			name:    "Default Redis Config",
			envVars: map[string]string{},
			expected: config.RedisConfig{
				Host: constants.DefaultRedisHost,
				Port: strconv.Itoa(constants.DefaultRedisPort),
				DB:   constants.DefaultRedisDB,
				SSL:  constants.DefaultRedisSSL,
			},
		},
		{
			name: "Custom Redis Config",
			envVars: map[string]string{
				constants.EnvRedisHost:     "redis.example.com",
				constants.EnvRedisPort:     "6380",
				constants.EnvRedisPassword: "secret",
				constants.EnvRedisDB:       "1",
				constants.EnvRedisSSL:      "true",
			},
			expected: config.RedisConfig{
				Host:     "redis.example.com",
				Port:     "6380",
				Password: "secret",
				DB:       1,
				SSL:      true,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Set environment variables
			for key, value := range tt.envVars {
				os.Setenv(key, value)
				defer os.Unsetenv(key)
			}

			// Load configuration
			cfg, err := config.Load()
			if err != nil {
				t.Fatalf("Failed to load configuration: %v", err)
			}

			// Verify Redis configuration
			if cfg.Redis.Host != tt.expected.Host {
				t.Errorf("Expected Redis host %s, got %s", tt.expected.Host, cfg.Redis.Host)
			}
			if cfg.Redis.Port != tt.expected.Port {
				t.Errorf("Expected Redis port %s, got %s", tt.expected.Port, cfg.Redis.Port)
			}
			if cfg.Redis.Password != tt.expected.Password {
				t.Errorf("Expected Redis password %s, got %s", tt.expected.Password, cfg.Redis.Password)
			}
			if cfg.Redis.DB != tt.expected.DB {
				t.Errorf("Expected Redis DB %d, got %d", tt.expected.DB, cfg.Redis.DB)
			}
			if cfg.Redis.SSL != tt.expected.SSL {
				t.Errorf("Expected Redis SSL %t, got %t", tt.expected.SSL, cfg.Redis.SSL)
			}
		})
	}
}

// TestMainEnvironmentVariables tests environment variable handling
func TestMainEnvironmentVariables(t *testing.T) {
	tests := []struct {
		name     string
		envVars  map[string]string
		expected string
	}{
		{
			name:     "Default Port",
			envVars:  map[string]string{},
			expected: "8080",
		},
		{
			name: "Custom Port",
			envVars: map[string]string{
				constants.EnvGatewayPort: "9090",
			},
			expected: "9090",
		},
		{
			name: "Custom Host",
			envVars: map[string]string{
				constants.EnvGatewayHost: "127.0.0.1",
			},
			expected: "127.0.0.1",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Set environment variables
			for key, value := range tt.envVars {
				os.Setenv(key, value)
				defer os.Unsetenv(key)
			}

			// Load configuration
			cfg, err := config.Load()
			if err != nil {
				t.Fatalf("Failed to load configuration: %v", err)
			}

			// Check if custom values are applied
			if tt.envVars[constants.EnvGatewayPort] != "" {
				if cfg.Server.Port != tt.expected {
					t.Errorf("Expected port %s, got %s", tt.expected, cfg.Server.Port)
				}
			}
			if tt.envVars[constants.EnvGatewayHost] != "" {
				if cfg.Server.Host != tt.expected {
					t.Errorf("Expected host %s, got %s", tt.expected, cfg.Server.Host)
				}
			}
		})
	}
}

// BenchmarkMainConfigurationLoading benchmarks the configuration loading
func BenchmarkMainConfigurationLoading(b *testing.B) {
	for i := 0; i < b.N; i++ {
		// Reset environment to defaults
		os.Unsetenv(constants.EnvGatewayPort)
		os.Unsetenv(constants.EnvGatewayHost)
		os.Unsetenv(constants.EnvRedisHost)
		os.Unsetenv(constants.EnvRedisPort)
		os.Unsetenv(constants.EnvUserServiceURL)
		os.Unsetenv(constants.EnvInventoryServiceURL)

		// Load configuration (this is what main() does)
		_, err := config.Load()
		if err != nil {
			b.Fatalf("Failed to load configuration: %v", err)
		}
	}
}

// TestMainFunctionality tests that main.go dependencies work correctly
// Note: This doesn't test main() directly, but tests the logic it uses
func TestMainFunctionality(t *testing.T) {
	t.Run("Configuration Loading Works", func(t *testing.T) {
		// Test that configuration can be loaded (main() dependency)
		cfg, err := config.Load()
		if err != nil {
			t.Errorf("Expected configuration to load successfully, got error: %v", err)
		}

		// Verify essential configuration is present
		if cfg.Server.Port == "" {
			t.Error("Expected server port to be set")
		}
		if cfg.Server.Host == "" {
			t.Error("Expected server host to be set")
		}
	})

	t.Run("Constants Are Defined", func(t *testing.T) {
		// Test that all constants used in main() are defined
		if constants.AppName == "" {
			t.Error("AppName should be defined")
		}
		if constants.AppVersion == "" {
			t.Error("AppVersion should be defined")
		}
		if constants.LogConfigLoadFailed == "" {
			t.Error("LogConfigLoadFailed should be defined")
		}
	})
}
