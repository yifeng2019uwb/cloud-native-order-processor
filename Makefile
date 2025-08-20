# Order Processor Development Makefile
# Complete development cycle automation

.PHONY: help clean build test deploy test-integration test-e2e dev-cycle quick-cycle

# Configuration
PROJECT_NAME := order-processor
DOCKER_REGISTRY := localhost:5000
K8S_NAMESPACE := order-processor
K8S_ENVIRONMENT := dev

# Service names
SERVICES := frontend gateway user-service inventory-service
DOCKER_IMAGES := $(addprefix order-processor-,$(SERVICES))

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Helper functions
log_info = @echo "$(BLUE)[INFO]$(NC) $1"
log_success = @echo "$(GREEN)[SUCCESS]$(NC) $1"
log_warning = @echo "$(YELLOW)[WARNING]$(NC) $1"
log_error = @echo "$(RED)[ERROR]$(NC) $1"

# Default target
help:
	@echo "$(BLUE)Order Processor Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Development Cycle:$(NC)"
	@echo "  dev-cycle          - Complete cycle: clean → build → test → deploy → integration-test"
	@echo "  quick-cycle        - Fast cycle: build → deploy → smoke-test"
	@echo "  test-local         - Local testing (mirrors CI/CD workflow)"
	@echo ""
	@echo "$(GREEN)Individual Steps:$(NC)"
	@echo "  clean              - Clean all build artifacts and containers"
	@echo "  build              - Build all components using new build scripts"
	@echo "  test               - Run unit tests for all components"
	@echo "  deploy             - Deploy to Kubernetes"
	@echo "  test-integration   - Run integration tests"
	@echo "  test-e2e           - Run end-to-end tests"
	@echo ""
	@echo "$(GREEN)Component-specific:$(NC)"
	@echo "  build-frontend     - Build frontend only"
	@echo "  build-gateway      - Build gateway only"
	@echo "  build-services     - Build backend services only"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  test-frontend      - Run frontend tests"
	@echo "  test-gateway       - Run gateway tests"
	@echo "  test-services      - Run backend services tests"
	@echo "  test-local-frontend - Local frontend testing"
	@echo "  test-local-gateway  - Local gateway testing"
	@echo "  test-local-services - Local backend services testing"
	@echo ""
	@echo "$(GREEN)Deployment:$(NC)"
	@echo "  deploy-docker      - Deploy using Docker Compose"
	@echo "  deploy-k8s         - Deploy to Kubernetes (includes port forwarding)"
	@echo "  port-forward       - Set up port forwarding for local access"
	@echo "  stop-port-forward  - Stop port forwarding"
	@echo ""
	@echo "$(GREEN)Monitoring:$(NC)"
	@echo "  logs               - Show logs for all services"
	@echo "  status             - Show deployment status"
	@echo "  health             - Check health of all services"
	@echo ""
	@echo "$(GREEN)CLI Tools:$(NC)"
	@echo "  cli-help           - Show CLI client help"
	@echo "  cli-test           - Test CLI client functionality"
	@echo ""
	@echo "$(GREEN)Compatibility (for CI/CD):$(NC)"
	@echo "  test-all           - Run all service tests (compatibility)"
	@echo "  build-all          - Build all services (compatibility)"
	@echo "  gateway-build      - Build gateway (compatibility)"
	@echo "  gateway-test       - Test gateway (compatibility)"
	@echo "  service-build      - Build specific service (compatibility)"
	@echo "  service-test       - Test specific service (compatibility)"

# Complete development cycle
dev-cycle: clean build test deploy test-integration
	$(call log_success,"Complete development cycle finished successfully!")
	$(call log_info,"Services are accessible at:")
	@echo "  Gateway: http://localhost:30000"
	@echo "  Frontend: http://localhost:30004"
	@echo "  CLI: ./scripts/cli-client.sh help"

# Quick development cycle (for rapid iteration)
quick-cycle: build deploy test-smoke
	$(call log_success,"Quick development cycle finished successfully!")
	$(call log_info,"Services are accessible at:")
	@echo "  Gateway: http://localhost:30000"
	@echo "  Frontend: http://localhost:30004"
	@echo "  CLI: ./scripts/cli-client.sh help"

# Local testing using test-local.sh script (mirrors CI/CD)
test-local:
	$(call log_info,"Running local tests (mirrors CI/CD)...")
	@./scripts/test-local.sh --environment dev --build
	$(call log_success,"Local tests completed")

# Component-specific local testing
test-local-frontend:
	$(call log_info,"Running local frontend tests...")
	@./scripts/test-local.sh --environment dev --frontend

test-local-gateway:
	$(call log_info,"Running local gateway tests...")
	@./scripts/test-local.sh --environment dev --gateway

test-local-services:
	$(call log_info,"Running local backend services tests...")
	@./scripts/test-local.sh --environment dev --services

# Clean everything
clean:
	$(call log_info,"Cleaning build artifacts and containers...")
	@docker system prune -f
	@docker volume prune -f
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "htmlcov*" -type d -exec rm -rf {} + 2>/dev/null || true
	$(call log_success,"Clean completed")

# Build all components using new build scripts
build: build-frontend build-gateway build-services
	$(call log_success,"All components built successfully")

# Build frontend using new dev.sh script
build-frontend:
	$(call log_info,"Building frontend...")
	@./frontend/dev.sh build
	$(call log_success,"Frontend built")

# Build gateway using new dev.sh script
build-gateway:
	$(call log_info,"Building gateway...")
	@./gateway/dev.sh build
	$(call log_success,"Gateway built")

# Build backend services using new dev.sh scripts
build-services:
	$(call log_info,"Building backend services...")
	@for service_dir in services/*/; do \
		if [ -d "$$service_dir" ] && [ -f "$$service_dir/dev.sh" ]; then \
			service_name=$$(basename "$$service_dir"); \
			echo "Building service: $$service_name"; \
			(cd "$$service_dir" && ./dev.sh build); \
		fi; \
	done
	$(call log_success,"Backend services built")

# Individual service builds (for compatibility)
build-user-service:
	$(call log_info,"Building user service...")
	@cd services/user_service && ./dev.sh build
	$(call log_success,"User service built")

build-inventory-service:
	$(call log_info,"Building inventory service...")
	@cd services/inventory_service && ./dev.sh build
	$(call log_success,"Inventory service built")

# Run all unit tests using new build scripts
test: test-frontend test-gateway test-services
	$(call log_success,"All unit tests passed")

# Test frontend using new dev.sh script
test-frontend:
	$(call log_info,"Running frontend tests...")
	@./frontend/dev.sh test

# Test gateway using new dev.sh script
test-gateway:
	$(call log_info,"Running gateway tests...")
	@./gateway/dev.sh test

# Test backend services using new dev.sh scripts
test-services:
	$(call log_info,"Running backend services tests...")
	@for service_dir in services/*/; do \
		if [ -d "$$service_dir" ] && [ -f "$$service_dir/dev.sh" ]; then \
			service_name=$$(basename "$$service_dir"); \
			echo "Testing service: $$service_name"; \
			(cd "$$service_dir" && ./dev.sh test); \
		fi; \
	done

# Individual service tests (for compatibility)
test-user-service:
	$(call log_info,"Running user service tests...")
	@cd services/user_service && ./dev.sh test

test-inventory-service:
	$(call log_info,"Running inventory service tests...")
	@cd services/inventory_service && ./dev.sh test

# Deploy to Kubernetes
deploy: deploy-k8s
	$(call log_success,"Deployment completed")

# Deploy to Kubernetes
deploy-k8s:
	$(call log_info,"Deploying to Kubernetes...")
	@kubectl cluster-info > /dev/null 2>&1 || (echo "Kubernetes cluster not available. Please start your cluster first." && exit 1)
	@kind load docker-image order-processor-frontend:latest --name order-processor || true
	@kind load docker-image order-processor-gateway:latest --name order-processor || true
	@kind load docker-image order-processor-user_service:latest --name order-processor || true
	@kind load docker-image order-processor-inventory_service:latest --name order-processor || true
	@kubectl apply -k kubernetes/base/
	@kubectl apply -k kubernetes/$(K8S_ENVIRONMENT)/
	@kubectl rollout restart deployment/frontend -n $(K8S_NAMESPACE)
	@kubectl rollout restart deployment/gateway -n $(K8S_NAMESPACE)
	@kubectl rollout restart deployment/user-service -n $(K8S_NAMESPACE)
	@kubectl rollout restart deployment/inventory-service -n $(K8S_NAMESPACE)
	$(call log_info,"Waiting for deployments to be ready...")
	@kubectl wait --for=condition=available --timeout=300s deployment/frontend -n $(K8S_NAMESPACE)
	@kubectl wait --for=condition=available --timeout=300s deployment/gateway -n $(K8S_NAMESPACE)
	@kubectl wait --for=condition=available --timeout=300s deployment/user-service -n $(K8S_NAMESPACE)
	@kubectl wait --for=condition=available --timeout=300s deployment/inventory-service -n $(K8S_NAMESPACE)
	$(call log_info,"Setting up port forwarding...")
	@pkill -f "kubectl port-forward" || true
	@kubectl port-forward svc/gateway 30000:8080 -n $(K8S_NAMESPACE) &
	@kubectl port-forward svc/frontend 30004:80 -n $(K8S_NAMESPACE) &
	@kubectl port-forward svc/user-service 30001:30001 -n $(K8S_NAMESPACE) &
	@kubectl port-forward svc/inventory-service 30002:30002 -n $(K8S_NAMESPACE) &
	@sleep 5
	$(call log_success,"Kubernetes deployment completed with port forwarding:")
	@echo "  Gateway: http://localhost:30000"
	@echo "  Frontend: http://localhost:30004"
	@echo "  User Service: http://localhost:30001"
	@echo "  Inventory Service: http://localhost:30002"

# Deploy using Docker Compose
deploy-docker:
	$(call log_info,"Deploying using Docker Compose...")
	@docker-compose -f docker/docker-compose.yml down
	@docker-compose -f docker/docker-compose.yml up -d --build
	$(call log_success,"Docker Compose deployment completed")

# Set up port forwarding
port-forward:
	$(call log_info,"Setting up port forwarding...")
	@pkill -f "kubectl port-forward" || true
	@kubectl port-forward svc/gateway 30000:8080 -n $(K8S_NAMESPACE) &
	@kubectl port-forward svc/frontend 30004:80 -n $(K8S_NAMESPACE) &
	@kubectl port-forward svc/user-service 30001:30001 -n $(K8S_NAMESPACE) &
	@kubectl port-forward svc/inventory-service 30002:30002 -n $(K8S_NAMESPACE) &
	@sleep 3
	$(call log_success,"Port forwarding set up:")
	@echo "  Gateway: http://localhost:30000"
	@echo "  Frontend: http://localhost:30004"
	@echo "  User Service: http://localhost:30001"
	@echo "  Inventory Service: http://localhost:30002"

# Run integration tests
test-integration:
	$(call log_info,"Running integration tests...")
	@cd integration_tests && python -m pytest -v
	$(call log_success,"Integration tests completed")

# Run end-to-end tests
test-e2e:
	$(call log_info,"Running end-to-end tests...")
	@cd integration_tests && python -m pytest test_e2e.py -v
	$(call log_success,"End-to-end tests completed")

# Run smoke tests (quick health checks)
test-smoke:
	$(call log_info,"Running smoke tests...")
	@./scripts/smoke-test.sh
	$(call log_success,"Smoke tests completed")

# Show logs
logs:
	$(call log_info,"Showing logs for all services...")
	@kubectl logs -f deployment/frontend -n $(K8S_NAMESPACE) &
	@kubectl logs -f deployment/gateway -n $(K8S_NAMESPACE) &
	@kubectl logs -f deployment/user-service -n $(K8S_NAMESPACE) &
	@kubectl logs -f deployment/inventory-service -n $(K8S_NAMESPACE) &
	@wait

# Show deployment status
status:
	$(call log_info,"Deployment status:")
	@kubectl get pods -n $(K8S_NAMESPACE)
	@echo ""
	@kubectl get services -n $(K8S_NAMESPACE)

# Check health of all services
health:
	$(call log_info,"Checking service health...")
	@curl -s http://localhost:30000/health | jq . || echo "Gateway health check failed"
	@curl -s http://localhost:30001/health | jq . || echo "User service health check failed"
	@curl -s http://localhost:30002/health | jq . || echo "Inventory service health check failed"

# CLI client help
cli-help:
	@./scripts/cli-client.sh help

# Test CLI client
cli-test:
	$(call log_info,"Testing CLI client...")
	@./scripts/cli-client.sh health
	@./scripts/cli-client.sh list-assets 3
	$(call log_success,"CLI client test completed")

# ====================
# COMPATIBILITY TARGETS (for CI/CD and documentation)
# These targets maintain backward compatibility with old build.sh scripts
# New development should use the dev.sh targets above
# ====================

# Backward compatibility for services Makefile
test-all:
	@echo "$(BLUE)[INFO]$(NC) Running all service tests (compatibility mode)..."
	@./services/build.sh --test-only -v

build-all:
	@echo "$(BLUE)[INFO]$(NC) Building all services (compatibility mode)..."
	@./services/build.sh -v

# Backward compatibility for old root Makefile commands
gateway-build:
	@echo "$(BLUE)[INFO]$(NC) Building gateway (compatibility mode)..."
	@./gateway/build.sh -v

gateway-test:
	@echo "$(BLUE)[INFO]$(NC) Testing gateway (compatibility mode)..."
	@./gateway/build.sh --test-only -v

gateway-dev:
	@echo "$(BLUE)[INFO]$(NC) Starting gateway development (compatibility mode)..."
	@cd gateway && ./dev.sh dev

service-build:
	@echo "$(BLUE)[INFO]$(NC) Building service $(SERVICE) (compatibility mode)..."
	@cd services && ./build.sh -v

service-test:
	@echo "$(BLUE)[INFO]$(NC) Testing service $(SERVICE) (compatibility mode)..."
	@cd services && ./build.sh --test-only -v

service-dev:
	@echo "$(BLUE)[INFO]$(NC) Starting service $(SERVICE) development (compatibility mode)..."
	@cd services/$(SERVICE) && python -m uvicorn src.main:app --reload --port 8000

tf-plan:
	@echo "$(BLUE)[INFO]$(NC) Creating Terraform plan (compatibility mode)..."
	@cd terraform && terraform plan

tf-apply:
	@echo "$(BLUE)[INFO]$(NC) Applying Terraform changes (compatibility mode)..."
	@cd terraform && terraform apply

clean-docker:
	@echo "$(BLUE)[INFO]$(NC) Cleaning Docker (compatibility mode)..."
	@docker system prune -f
	@docker volume prune -f

deploy-full:
	@echo "$(BLUE)[INFO]$(NC) Full deployment (compatibility mode)..."
	@make dev-cycle

# Development environment setup
setup-dev:
	$(call log_info,"Setting up development environment...")
	@./scripts/setup-dev.sh
	$(call log_success,"Development environment setup completed")

# Cleanup development environment
cleanup-dev:
	$(call log_info,"Cleaning up development environment...")
	@pkill -f "kubectl port-forward" || true
	@kubectl delete namespace $(K8S_NAMESPACE) --ignore-not-found=true
	@docker-compose -f docker/docker-compose.yml down -v
	@docker system prune -f
	$(call log_success,"Development environment cleaned up")

# Stop port forwarding
stop-port-forward:
	$(call log_info,"Stopping port forwarding...")
	@pkill -f "kubectl port-forward" || true
	$(call log_success,"Port forwarding stopped")
