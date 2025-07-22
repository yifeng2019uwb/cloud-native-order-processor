package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
	"github.com/golang-jwt/jwt/v4"
)

// Configuration
type Config struct {
	Port         string
	RedisHost    string
	RedisPort    string
	RedisDB      int
	JWTSecret    string
	UserService  string
	InventoryService string
}

// Redis client
var rdb *redis.Client
var ctx = context.Background()

// JWT Claims
type Claims struct {
	UserID   string `json:"user_id"`
	Username string `json:"username"`
	jwt.RegisteredClaims
}

// Rate limiting
type RateLimit struct {
	Requests int
	Window   time.Duration
}

// Initialize configuration
func getConfig() *Config {
	return &Config{
		Port:         getEnv("GATEWAY_PORT", "8080"),
		RedisHost:    getEnv("REDIS_HOST", "redis"),
		RedisPort:    getEnv("REDIS_PORT", "6379"),
		RedisDB:      0,
		JWTSecret:    getEnv("JWT_SECRET", "your-secret-key"),
		UserService:  getEnv("USER_SERVICE_URL", "http://user_service:8000"),
		InventoryService: getEnv("INVENTORY_SERVICE_URL", "http://inventory_service:8001"),
	}
}

// Get environment variable with default
func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// Initialize Redis connection
func initRedis(config *Config) {
	rdb = redis.NewClient(&redis.Options{
		Addr:     fmt.Sprintf("%s:%s", config.RedisHost, config.RedisPort),
		DB:       config.RedisDB,
		Password: "", // no password set
	})

	// Test Redis connection
	_, err := rdb.Ping(ctx).Result()
	if err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}
	log.Println("✅ Connected to Redis")
}

// Authentication middleware
func authMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Skip auth for health checks and public endpoints
		if c.Request.URL.Path == "/health" || c.Request.URL.Path == "/auth/login" || c.Request.URL.Path == "/auth/register" {
			c.Next()
			return
		}

		// Get token from header
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
			c.Abort()
			return
		}

		// Extract token
		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenString == authHeader {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Bearer token required"})
			c.Abort()
			return
		}

		// Check if token is blacklisted in Redis
		isBlacklisted, err := rdb.Exists(ctx, fmt.Sprintf("blacklist:%s", tokenString)).Result()
		if err != nil {
			log.Printf("Redis error checking blacklist: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			c.Abort()
			return
		}

		if isBlacklisted == 1 {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Token has been revoked"})
			c.Abort()
			return
		}

		// Validate JWT token
		token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
			return []byte(getConfig().JWTSecret), nil
		})

		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
			c.Abort()
			return
		}

		// Extract claims
		claims, ok := token.Claims.(*Claims)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token claims"})
			c.Abort()
			return
		}

		// Store user info in context
		c.Set("user_id", claims.UserID)
		c.Set("username", claims.Username)

		c.Next()
	}
}

// Rate limiting middleware
func rateLimitMiddleware(limit int, window time.Duration) gin.HandlerFunc {
	return func(c *gin.Context) {
		userID := c.GetString("user_id")
		if userID == "" {
			userID = c.ClientIP() // Use IP for unauthenticated requests
		}

		key := fmt.Sprintf("ratelimit:%s:%s", userID, c.Request.URL.Path)

		// Get current count
		count, err := rdb.Get(ctx, key).Int()
		if err != nil && err != redis.Nil {
			log.Printf("Redis error getting rate limit: %v", err)
			c.Next()
			return
		}

		if count >= limit {
			c.JSON(http.StatusTooManyRequests, gin.H{
				"error": "Rate limit exceeded",
				"retry_after": window.Seconds(),
			})
			c.Abort()
			return
		}

		// Increment counter
		pipe := rdb.Pipeline()
		pipe.Incr(ctx, key)
		pipe.Expire(ctx, key, window)
		_, err = pipe.Exec(ctx)
		if err != nil {
			log.Printf("Redis error setting rate limit: %v", err)
		}

		c.Next()
	}
}

// Caching middleware
func cacheMiddleware(ttl time.Duration) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Only cache GET requests
		if c.Request.Method != "GET" {
			c.Next()
			return
		}

		// Generate cache key
		cacheKey := fmt.Sprintf("cache:%s:%s", c.Request.Method, c.Request.URL.String())

		// Try to get from cache
		cached, err := rdb.Get(ctx, cacheKey).Result()
		if err == nil {
			// Return cached response
			var response map[string]interface{}
			if err := json.Unmarshal([]byte(cached), &response); err == nil {
				c.JSON(http.StatusOK, response)
				c.Abort()
				return
			}
		}

		// Store original response writer
		originalWriter := c.Writer
		c.Writer = &responseWriter{ResponseWriter: originalWriter, body: []byte{}}

		c.Next()

		// Cache the response if it's successful
		if c.Writer.Status() == http.StatusOK {
			responseData := map[string]interface{}{
				"status": c.Writer.Status(),
				"body":   string(c.Writer.(*responseWriter).body),
			}

			responseJSON, _ := json.Marshal(responseData)
			rdb.Set(ctx, cacheKey, responseJSON, ttl)
		}
	}
}

// Custom response writer for caching
type responseWriter struct {
	gin.ResponseWriter
	body []byte
}

func (w *responseWriter) Write(b []byte) (int, error) {
	w.body = append(w.body, b...)
	return w.ResponseWriter.Write(b)
}

// Proxy requests to services
func proxyToService(serviceURL string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Create request to backend service
		req, err := http.NewRequest(c.Request.Method, serviceURL+c.Request.URL.Path, c.Request.Body)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request"})
			return
		}

		// Copy headers
		for key, values := range c.Request.Header {
			for _, value := range values {
				req.Header.Add(key, value)
			}
		}

		// Make request to backend
		client := &http.Client{Timeout: 30 * time.Second}
		resp, err := client.Do(req)
		if err != nil {
			c.JSON(http.StatusBadGateway, gin.H{"error": "Backend service unavailable"})
			return
		}
		defer resp.Body.Close()

		// Copy response headers
		for key, values := range resp.Header {
			for _, value := range values {
				c.Header(key, value)
			}
		}

		// Set status and copy body
		c.Status(resp.StatusCode)
		c.DataFromReader(resp.StatusCode, resp.ContentLength, resp.Header.Get("Content-Type"), resp.Body, nil)
	}
}

// Health check endpoint
func healthCheck(c *gin.Context) {
	// Check Redis connection
	_, err := rdb.Ping(ctx).Result()
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{
			"status": "unhealthy",
			"error":  "Redis connection failed",
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
		"service": "api-gateway",
		"timestamp": time.Now().UTC(),
	})
}

// Logout endpoint (blacklist token)
func logout(c *gin.Context) {
	userID := c.GetString("user_id")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
		return
	}

	// Get token from header
	authHeader := c.GetHeader("Authorization")
	tokenString := strings.TrimPrefix(authHeader, "Bearer ")

	// Blacklist token in Redis (24 hour expiry)
	key := fmt.Sprintf("blacklist:%s", tokenString)
	err := rdb.Set(ctx, key, "revoked", 24*time.Hour).Err()
	if err != nil {
		log.Printf("Redis error blacklisting token: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to logout"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Successfully logged out"})
}

func main() {
	config := getConfig()

	// Initialize Redis
	initRedis(config)

	// Set Gin mode
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	// Health check
	r.GET("/health", healthCheck)

	// Auth routes (no auth required)
	auth := r.Group("/auth")
	{
		auth.POST("/login", proxyToService(config.UserService))
		auth.POST("/register", proxyToService(config.UserService))
		auth.POST("/logout", authMiddleware(), logout)
	}

	// Protected routes
	protected := r.Group("/")
	protected.Use(authMiddleware())
	protected.Use(rateLimitMiddleware(100, time.Minute)) // 100 requests per minute
	{
		// User service routes
		user := protected.Group("/auth")
		{
			user.GET("/me", cacheMiddleware(5*time.Minute), proxyToService(config.UserService))
		}

		// Inventory service routes
		inventory := protected.Group("/inventory")
		{
			inventory.GET("/assets", cacheMiddleware(1*time.Minute), proxyToService(config.InventoryService))
			inventory.GET("/assets/:id", cacheMiddleware(5*time.Minute), proxyToService(config.InventoryService))
		}
	}

	log.Printf("🚀 API Gateway starting on port %s", config.Port)
	log.Printf("📡 User Service: %s", config.UserService)
	log.Printf("📡 Inventory Service: %s", config.InventoryService)
	log.Printf("🔴 Redis: %s:%s", config.RedisHost, config.RedisPort)

	if err := r.Run(":" + config.Port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}