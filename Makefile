# Makefile for Cloud Native Order Processor
# Provides convenient shortcuts for common development operations

.PHONY: help install test build deploy clean terraform docker k8s frontend backend

# Default target
help:
	@echo "Cloud Native Order Processor - Development Commands"
	@echo ""
	@echo "📦 INSTALLATION:"
	@echo "  install          Install all dependencies"
	@echo "  install-frontend Install frontend dependencies"
	@echo "  install-backend  Install backend dependencies"
	@echo ""
	@echo "🧪 TESTING:"
	@echo "  test             Run all tests"
	@echo "  test-frontend    Run frontend tests"
	@echo "  test-backend     Run backend tests"
	@echo "  test-infra       Run infrastructure tests"
	@echo ""
	@echo "🏗️  BUILDING:"
	@echo "  build            Build all services"
	@echo "  build-frontend   Build frontend"
	@echo "  build-backend    Build backend services"
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
	@echo "  test-service     Test specific service (SERVICE=name)"
	@echo "  test-integration Run full integration tests"
	@echo ""
	@echo "📊 MONITORING:"
	@echo "  monitor-start    Start monitoring stack"
	@echo "  monitor-stop     Stop monitoring stack"
	@echo "  monitor-logs     Show monitoring logs"

# ====================
# INSTALLATION
# ====================

install: install-frontend install-backend
	@echo "✅ All dependencies installed"

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install

install-backend:
	@echo "📦 Installing backend dependencies..."
	cd services && make install-all

# ====================
# TESTING
# ====================

test: test-backend test-frontend test-infra
	@echo "✅ All tests completed"

test-frontend:
	@echo "🧪 Running frontend tests..."
	@echo "⚠️  Frontend tests not configured yet - skipping"
	@echo "   To add tests, install testing framework (e.g., Vitest, Jest) and add test script to package.json"

test-backend:
	@echo "🧪 Running backend tests..."
	cd services && make test-all

test-infra:
	@echo "🧪 Running infrastructure tests..."
	cd terraform && ./scripts/terraform-ops.sh test

# ====================
# BUILDING
# ====================

build: build-backend build-frontend
	@echo "✅ All services built"

build-frontend:
	@echo "🏗️  Building frontend..."
	cd frontend && npm run build

build-backend:
	@echo "🏗️  Building backend services..."
	cd services && make build-all

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

# Quick test for what you're working on
test-service:
	@echo "🧪 Running tests for current service..."
	@echo "Usage: make test-service SERVICE=user_service"
	@if [ -z "$(SERVICE)" ]; then \
		echo "Please specify SERVICE=user_service or SERVICE=inventory_service"; \
		exit 1; \
	fi
	cd services && make test SERVICE=$(SERVICE)

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
# UTILITY TARGETS
# ====================

# Quick development workflow
dev: dev-setup dev-start
	@echo "🎉 Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "User Service: http://localhost:8001"
	@echo "Inventory Service: http://localhost:8002"

# Full deployment workflow
full-deploy: test build deploy
	@echo "🎉 Full deployment completed!"

# Quick local testing
quick-test: test-backend test-frontend
	@echo "✅ Quick tests completed"

# Format code
format:
	@echo "🎨 Formatting code..."
	cd frontend && npm run format
	cd terraform && terraform fmt -recursive

# Lint code
lint:
	@echo "🔍 Linting code..."
	cd frontend && npm run lint
	cd terraform && terraform validate
