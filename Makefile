# Makefile for Cloud Native Order Processor
# Provides convenient shortcuts for common development operations

.PHONY: help install test build deploy clean terraform docker k8s frontend backend gateway

# Default target
help:
	@echo "Cloud Native Order Processor - Development Commands"
	@echo ""
	@echo "📦 INSTALLATION:"
	@echo "  install          Install all dependencies"
	@echo "  install-frontend Install frontend dependencies"
	@echo "  install-backend  Install backend dependencies"
	@echo "  install-gateway  Install gateway dependencies"
	@echo ""
	@echo "🧪 TESTING:"
	@echo "  test             Run all tests"
	@echo "  test-frontend    Run frontend tests"
	@echo "  test-backend     Run backend tests"
	@echo "  test-gateway     Run gateway tests"
	@echo "  test-infra       Run infrastructure tests"
	@echo ""
	@echo "🏗️  BUILDING:"
	@echo "  build            Build all services"
	@echo "  build-frontend   Build frontend"
	@echo "  build-backend    Build backend services"
	@echo "  build-gateway    Build gateway"
	@echo "  build-docker     Build Docker images"
	@echo ""
	@echo "🚀 DEPLOYMENT:"
	@echo "  deploy           Deploy to local environment"
	@echo "  deploy-dev       Deploy to development environment"
	@echo "  deploy-prod      Deploy to production environment"
	@echo ""
	@echo "🗑️  CLEANUP:"
	@echo "  clean            Clean all build artifacts"
	@echo "  clean-docker     Clean Docker images"
	@echo "  clean-terraform  Clean Terraform state"
	@echo ""
	@echo "☁️  TERRAFORM:"
	@echo "  tf-init          Initialize Terraform"
	@echo "  tf-plan          Create Terraform plan"
	@echo "  tf-apply         Apply Terraform changes"
	@echo "  tf-destroy       Destroy Terraform resources"
	@echo "  tf-validate      Validate Terraform configuration"
	@echo ""
	@echo "🐳 DOCKER:"
	@echo "  docker-build     Build all Docker images"
	@echo "  docker-up        Start Docker Compose"
	@echo "  docker-down      Stop Docker Compose"
	@echo "  docker-logs      Show Docker logs"
	@echo ""
	@echo "☸️  KUBERNETES:"
	@echo "  k8s-deploy       Deploy to Kubernetes"
	@echo "  k8s-delete       Delete from Kubernetes"
	@echo "  k8s-logs         Show Kubernetes logs"
	@echo "  k8s-port-forward Port forward services"
	@echo ""
	@echo "🔧 DEVELOPMENT:"
	@echo "  dev-setup        Setup development environment"
	@echo "  dev-user-service Start user service for development"
	@echo "  dev-inventory-service Start inventory service for development"
	@echo "  dev-frontend     Start frontend for development"
	@echo "  dev-gateway      Start gateway for development"
	@echo "  test-service     Test specific service (SERVICE=name)"
	@echo "  test-integration Run full integration tests"
	@echo ""
	@echo "📊 MONITORING:"
	@echo "  monitor-start    Start monitoring stack"
	@echo "  monitor-stop     Stop monitoring stack"
	@echo "  monitor-logs     Show monitoring logs"
	@echo ""
	@echo "🎯 QUICK COMMANDS:"
	@echo "  dev              Quick development setup and start"
	@echo "  quick-build      Build current component (auto-detected)"
	@echo "  quick-test       Test current component (auto-detected)"
	@echo "  quick-run        Run current component (auto-detected)"

# ====================
# INSTALLATION
# ====================

install: install-frontend install-backend install-gateway
	@echo "✅ All dependencies installed"

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install

install-backend:
	@echo "📦 Installing backend dependencies..."
	cd services && make install-all

install-gateway:
	@echo "📦 Installing gateway dependencies..."
	cd gateway && ./dev.sh install

# ====================
# TESTING
# ====================

test: test-backend test-frontend test-gateway test-infra
	@echo "✅ All tests completed"

test-frontend:
	@echo "🧪 Running frontend tests..."
	@echo "⚠️  Frontend tests not configured yet - skipping"
	@echo "   To add tests, install testing framework (e.g., Vitest, Jest) and add test script to package.json"

test-backend:
	@echo "🧪 Running backend tests..."
	cd services && make test-all

test-gateway:
	@echo "🧪 Running gateway tests..."
	cd gateway && ./dev.sh test

test-infra:
	@echo "🧪 Running infrastructure tests..."
	cd terraform && ./scripts/terraform-ops.sh test

# ====================
# BUILDING
# ====================

build: build-backend build-frontend build-gateway
	@echo "✅ All services built"

build-frontend:
	@echo "🏗️  Building frontend..."
	cd frontend && npm run build

build-backend:
	@echo "🏗️  Building backend services..."
	cd services && make build-all

build-gateway:
	@echo "🏗️  Building gateway..."
	cd gateway && ./dev.sh build

build-docker:
	@echo "🐳 Building Docker images..."
	docker-compose -f docker/docker-compose.yml build

# ====================
# DEPLOYMENT
# ====================

deploy: deploy-dev

deploy-dev:
	@echo "🚀 Deploying to development environment..."
	./scripts/deploy.sh --environment dev

deploy-prod:
	@echo "🚀 Deploying to production environment..."
	./scripts/deploy.sh --environment prod

# ====================
# CLEANUP
# ====================

clean: clean-docker clean-terraform
	@echo "🧹 Cleaning build artifacts..."
	rm -rf frontend/dist
	rm -rf services/*/build
	rm -rf services/*/dist
	rm -rf services/*/htmlcov-*
	rm -rf services/*/*.egg-info
	rm -rf gateway/gateway
	rm -rf gateway/coverage
	@echo "✅ Cleanup completed"

clean-docker:
	@echo "🐳 Cleaning Docker images..."
	docker-compose -f docker/docker-compose.yml down --rmi all
	docker system prune -f

clean-terraform:
	@echo "☁️  Cleaning Terraform state..."
	cd terraform && ./scripts/terraform-ops.sh clean --auto-approve

# ====================
# TERRAFORM
# ====================

tf-init:
	@echo "☁️  Initializing Terraform..."
	cd terraform && ./scripts/terraform-ops.sh init

tf-plan:
	@echo "☁️  Creating Terraform plan..."
	cd terraform && ./scripts/terraform-ops.sh plan

tf-apply:
	@echo "☁️  Applying Terraform changes..."
	cd terraform && ./scripts/terraform-ops.sh apply

tf-destroy:
	@echo "☁️  Destroying Terraform resources..."
	cd terraform && ./scripts/terraform-ops.sh destroy

tf-validate:
	@echo "☁️  Validating Terraform configuration..."
	cd terraform && ./scripts/terraform-ops.sh validate

# ====================
# DOCKER
# ====================

docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose -f docker/docker-compose.yml build

docker-up:
	@echo "🐳 Starting Docker Compose..."
	docker-compose -f docker/docker-compose.yml up -d

docker-down:
	@echo "🐳 Stopping Docker Compose..."
	docker-compose -f docker/docker-compose.yml down

docker-logs:
	@echo "🐳 Showing Docker logs..."
	docker-compose -f docker/docker-compose.yml logs -f

# Development Docker commands
docker-dev-build:
	@echo "🐳 Building Docker images for development..."
	docker-compose -f docker/docker-compose.dev.yml build

docker-dev-up:
	@echo "🐳 Starting Docker Compose for development..."
	docker-compose -f docker/docker-compose.dev.yml up -d

docker-dev-down:
	@echo "🐳 Stopping Docker Compose for development..."
	docker-compose -f docker/docker-compose.dev.yml down

docker-dev-logs:
	@echo "🐳 Showing Docker logs for development..."
	docker-compose -f docker/docker-compose.dev.yml logs -f

docker-gateway-logs:
	@echo "🐳 Showing Gateway logs..."
	docker-compose -f docker/docker-compose.dev.yml logs -f gateway

# ====================
# KUBERNETES
# ====================

k8s-deploy:
	@echo "☸️  Deploying to Kubernetes..."
	cd kubernetes && ./deploy.sh

k8s-delete:
	@echo "☸️  Deleting from Kubernetes..."
	cd kubernetes && ./cleanup.sh

k8s-logs:
	@echo "☸️  Showing Kubernetes logs..."
	kubectl logs -f -l app=order-processor

k8s-port-forward:
	@echo "☸️  Setting up port forwarding..."
	kubectl port-forward svc/frontend 3000:80 &
	kubectl port-forward svc/user-service 8001:8000 &
	kubectl port-forward svc/inventory-service 8002:8000 &

# ====================
# DEVELOPMENT
# ====================

# Quick development workflow - focus on what you're working on
dev-setup: install
	@echo "🔧 Setting up development environment..."
	./scripts/validate-environment.sh
	@echo "✅ Development environment ready"

# Start individual services for focused development
dev-user-service:
	@echo "🚀 Starting user service for development..."
	cd services/user_service && python -m uvicorn src.main:app --reload --port 8001

dev-inventory-service:
	@echo "🚀 Starting inventory service for development..."
	cd services/inventory_service && python -m uvicorn src.main:app --reload --port 8002

dev-frontend:
	@echo "🚀 Starting frontend for development..."
	cd frontend && npm run dev

dev-gateway:
	@echo "🚀 Starting gateway for development..."
	cd gateway && ./dev.sh dev

# Quick test for what you're working on
test-service:
	@echo "🧪 Running tests for current service..."
	@echo "Usage: make test-service SERVICE=user_service"
	@if [ -z "$(SERVICE)" ]; then \
		echo "Please specify SERVICE=user_service, SERVICE=inventory_service, or SERVICE=gateway"; \
		exit 1; \
	fi
	@if [ "$(SERVICE)" = "gateway" ]; then \
		cd gateway && ./dev.sh test; \
	else \
		cd services && make test SERVICE=$(SERVICE); \
	fi

# Integration test when needed
test-integration:
	@echo "🧪 Running integration tests..."
	./scripts/test-local.sh --environment dev --full-test

# ====================
# MONITORING
# ====================

monitor-start:
	@echo "📊 Starting monitoring stack..."
	docker-compose -f monitoring/docker-compose.yml up -d

monitor-stop:
	@echo "📊 Stopping monitoring stack..."
	docker-compose -f monitoring/docker-compose.yml down

monitor-logs:
	@echo "📊 Showing monitoring logs..."
	docker-compose -f monitoring/docker-compose.yml logs -f

# ====================
# QUICK COMMANDS (Auto-Detection)
# ====================

# Auto-detect current component and run appropriate command
quick-build:
	@echo "🔍 Auto-detecting component for build..."
	@if [ -f "frontend/package.json" ] && [ "$(PWD)" = "$(realpath frontend)" ]; then \
		echo "📦 Building frontend..."; \
		npm run build; \
	elif [ -f "gateway/go.mod" ] && [ "$(PWD)" = "$(realpath gateway)" ]; then \
		echo "🏗️  Building gateway..."; \
		./dev.sh build; \
	elif [ -f "services/Makefile" ] && [ "$(PWD)" = "$(realpath services)" ]; then \
		echo "🐍 Building backend services..."; \
		make build-all; \
	elif [ -f "services/user_service/setup.py" ] && [ "$(PWD)" = "$(realpath services/user_service)" ]; then \
		echo "🐍 Building user service..."; \
		../build.sh --build-only user_service; \
	elif [ -f "services/inventory_service/setup.py" ] && [ "$(PWD)" = "$(realpath services/inventory_service)" ]; then \
		echo "🐍 Building inventory service..."; \
		../build.sh --build-only inventory_service; \
	else \
		echo "❌ No supported component detected in current directory"; \
		echo "Supported: frontend/, gateway/, services/, services/user_service/, services/inventory_service/"; \
		exit 1; \
	fi

quick-test:
	@echo "🔍 Auto-detecting component for testing..."
	@if [ -f "frontend/package.json" ] && [ "$(PWD)" = "$(realpath frontend)" ]; then \
		echo "🧪 Testing frontend..."; \
		npm test 2>/dev/null || echo "⚠️  No test script configured"; \
	elif [ -f "gateway/go.mod" ] && [ "$(PWD)" = "$(realpath gateway)" ]; then \
		echo "🧪 Testing gateway..."; \
		./dev.sh test; \
	elif [ -f "services/Makefile" ] && [ "$(PWD)" = "$(realpath services)" ]; then \
		echo "🧪 Testing backend services..."; \
		make test-all; \
	elif [ -f "services/user_service/setup.py" ] && [ "$(PWD)" = "$(realpath services/user_service)" ]; then \
		echo "🧪 Testing user service..."; \
		../build.sh --test-only user_service; \
	elif [ -f "services/inventory_service/setup.py" ] && [ "$(PWD)" = "$(realpath services/inventory_service)" ]; then \
		echo "🧪 Testing inventory service..."; \
		../build.sh --test-only inventory_service; \
	else \
		echo "❌ No supported component detected in current directory"; \
		echo "Supported: frontend/, gateway/, services/, services/user_service/, services/inventory_service/"; \
		exit 1; \
	fi

quick-run:
	@echo "🔍 Auto-detecting component for running..."
	@if [ -f "frontend/package.json" ] && [ "$(PWD)" = "$(realpath frontend)" ]; then \
		echo "🚀 Running frontend..."; \
		npm run dev; \
	elif [ -f "gateway/go.mod" ] && [ "$(PWD)" = "$(realpath gateway)" ]; then \
		echo "🚀 Running gateway..."; \
		./dev.sh run; \
	elif [ -f "services/user_service/setup.py" ] && [ "$(PWD)" = "$(realpath services/user_service)" ]; then \
		echo "🚀 Running user service..."; \
		python -m uvicorn src.main:app --reload --port 8001; \
	elif [ -f "services/inventory_service/setup.py" ] && [ "$(PWD)" = "$(realpath services/inventory_service)" ]; then \
		echo "🚀 Running inventory service..."; \
		python -m uvicorn src.main:app --reload --port 8002; \
	else \
		echo "❌ No supported component detected in current directory"; \
		echo "Supported: frontend/, gateway/, services/user_service/, services/inventory_service/"; \
		exit 1; \
	fi

# ====================
# UTILITY TARGETS
# ====================

# Quick development workflow
dev: dev-setup docker-dev-up
	@echo "🎉 Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "User Service: http://localhost:8000"
	@echo "Inventory Service: http://localhost:8001"
	@echo "Gateway: http://localhost:8080"
	@echo "API Gateway: http://localhost:8080/api/v1/*"

# Full deployment workflow
full-deploy: test build deploy
	@echo "🎉 Full deployment completed!"

# Quick local testing
quick-test: test-backend test-frontend test-gateway
	@echo "✅ Quick tests completed"

# Format code
format:
	@echo "🎨 Formatting code..."
	cd frontend && npm run format 2>/dev/null || echo "⚠️  No format script in frontend"
	cd gateway && ./dev.sh format
	cd terraform && terraform fmt -recursive

# Lint code
lint:
	@echo "🔍 Linting code..."
	cd frontend && npm run lint 2>/dev/null || echo "⚠️  No lint script in frontend"
	cd gateway && ./dev.sh lint
	cd terraform && terraform validate
