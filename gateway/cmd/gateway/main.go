package main

import (
	"log"

	"order-processor-gateway/internal/api"
	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/services"
	"order-processor-gateway/pkg/constants"
)

func main() {
	// Log application startup
	log.Printf("🚀 Starting %s v%s", constants.AppName, constants.AppVersion)

	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("%s: %v", constants.LogConfigLoadFailed, err)
	}

	// Initialize Redis service
	redisService, err := services.NewRedisService(&cfg.Redis)
	if err != nil {
		log.Printf("Warning: %s: %v", constants.LogRedisConnectFailed, err)
		log.Println(constants.LogRedisContinueWithout)
		redisService = nil
	} else {
		defer redisService.Close()
		log.Printf("✅ %s", constants.LogRedisConnectSuccess)
	}

	// Initialize proxy service
	proxyService := services.NewProxyService(cfg)
	log.Printf("✅ %s", constants.LogProxyInitSuccess)

	// Initialize and start the API server
	server := api.NewServer(cfg, redisService, proxyService)

	log.Printf("🚀 %s %s", constants.LogServerStart, cfg.Server.Port)
	if err := server.Start(); err != nil {
		log.Fatalf("%s: %v", constants.LogServerStartFailed, err)
	}
}
