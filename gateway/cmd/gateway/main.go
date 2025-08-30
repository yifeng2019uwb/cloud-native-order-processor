package main

import (
	"log"

	"order-processor-gateway/internal/api"
	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"
	"order-processor-gateway/pkg/logging"
)

func main() {
	// Initialize structured logger
	logger := logging.NewBaseLogger(logging.GATEWAY)

	// Log application startup
	logger.Info(logging.STARTUP, "Starting Gateway service", "", map[string]interface{}{
		"app_name":    constants.AppName,
		"app_version": constants.AppVersion,
	})

	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		logger.Error(logging.STARTUP, "Configuration load failed", "", map[string]interface{}{
			"error": err.Error(),
		})
		log.Fatalf("%s: %v", constants.LogConfigLoadFailed, err)
	}

	// Initialize Redis service
	redisService, err := services.NewRedisService(&cfg.Redis)
	if err != nil {
		logger.Warning(logging.STARTUP, "Redis connection failed", "", map[string]interface{}{
			"error": err.Error(),
		})
		redisService = nil
	} else {
		defer redisService.Close()
		logger.Info(logging.STARTUP, "Redis connection successful", "", nil)
	}

	// Initialize proxy service
	proxyService := services.NewProxyService(cfg)
	logger.Info(logging.STARTUP, "Proxy service initialized", "", nil)

	// Initialize and start the API server
	server := api.NewServer(cfg, redisService, proxyService)

	logger.Info(logging.STARTUP, "Starting HTTP server", "", map[string]interface{}{
		"port": cfg.Server.Port,
	})

	if err := server.Start(); err != nil {
		logger.Error(logging.STARTUP, "Server start failed", "", map[string]interface{}{
			"error": err.Error(),
			"port":  cfg.Server.Port,
		})
		log.Fatalf("%s: %v", constants.LogServerStartFailed, err)
	}
}
