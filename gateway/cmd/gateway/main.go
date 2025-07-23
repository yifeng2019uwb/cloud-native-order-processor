package main

import (
	"log"

	"order-processor-gateway/internal/api"
	"order-processor-gateway/internal/config"
	"order-processor-gateway/internal/services"
)

func main() {
	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Initialize Redis service
	// TODO: Add proper error handling and connection pooling
	redisService, err := services.NewRedisService(&cfg.Redis)
	if err != nil {
		log.Printf("Warning: Failed to connect to Redis: %v", err)
		log.Println("Continuing without Redis (some features will be disabled)")
		redisService = nil
	} else {
		defer redisService.Close()
		log.Println("✅ Connected to Redis")
	}

	// Initialize proxy service
	proxyService := services.NewProxyService(cfg)
	log.Println("✅ Proxy service initialized")

	// Initialize and start the API server
	server := api.NewServer(cfg, redisService, proxyService)

	log.Printf("🚀 Starting Gateway server on port %s", cfg.Server.Port)
	if err := server.Start(); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
