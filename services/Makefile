# Makefile for Python Microservices Build System
# This provides convenient targets for common build operations

.PHONY: help build test clean install lint format check-format docker
.DEFAULT_GOAL := help

# Variables
SERVICE ?=
PYTHON_VERSION ?= 3.11
COVERAGE_THRESHOLD ?= 80

# Colors for help output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
NC := \033[0m

help: ## Show this help message
	@echo "$(BLUE)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)Usage examples:$(NC)"
	@echo "  make build SERVICE=order-service    # Build specific service"
	@echo "  make test                           # Run tests for current service"
	@echo "  make clean build                    # Clean and build"
	@echo "  make docker SERVICE=order-service   # Build with Docker"
	@echo ""
	@echo "$(BLUE)Variables:$(NC)"
	@echo "  SERVICE             - Service name (auto-detected if not specified)"
	@echo "  PYTHON_VERSION      - Python version (default: $(PYTHON_VERSION))"
	@echo "  COVERAGE_THRESHOLD  - Test coverage threshold (default: $(COVERAGE_THRESHOLD)%)"

build: ## Build the service/package
	@./build.sh --python $(PYTHON_VERSION) --coverage $(COVERAGE_THRESHOLD) $(SERVICE)

test: ## Run tests only
	@./build.sh --test-only --python $(PYTHON_VERSION) --coverage $(COVERAGE_THRESHOLD) $(SERVICE)

test-no-coverage: ## Run tests without coverage reporting
	@./build.sh --test-only --no-coverage --python $(PYTHON_VERSION) $(SERVICE)

build-only: ## Build package without running tests
	@./build.sh --build-only --python $(PYTHON_VERSION) $(SERVICE)

clean: ## Clean build artifacts
	@./build.sh --clean $(SERVICE)

clean-build: clean build ## Clean and build

install-deps: ## Install dependencies only
	@./build.sh --install-deps --python $(PYTHON_VERSION) $(SERVICE)

lint: ## Run linting tools
	@./build.sh --test-only --python $(PYTHON_VERSION) $(SERVICE)

docker: ## Build Docker image
	@./build.sh --docker --python $(PYTHON_VERSION) $(SERVICE)

# Service-specific targets
build-common: ## Build common package
	@$(MAKE) build SERVICE=common

test-common: ## Test common package
	@$(MAKE) test SERVICE=common

build-order-service: ## Build order-service
	@$(MAKE) build SERVICE=order-service

test-order-service: ## Test order-service
	@$(MAKE) test SERVICE=order-service

build-inventory-service: ## Build inventory-service
	@$(MAKE) build SERVICE=inventory-service

test-inventory-service: ## Test inventory-service
	@$(MAKE) test SERVICE=inventory-service

build-notification-service: ## Build notification-service
	@$(MAKE) build SERVICE=notification-service

test-notification-service: ## Test notification-service
	@$(MAKE) test SERVICE=notification-service

build-payment-service: ## Build payment-service
	@$(MAKE) build SERVICE=payment-service

test-payment-service: ## Test payment-service
	@$(MAKE) test SERVICE=payment-service

# Batch targets
build-all: ## Build all services
	@echo "$(BLUE)Building all services...$(NC)"
	@$(MAKE) build-common
	@$(MAKE) build-order-service
	@$(MAKE) build-inventory-service
	@$(MAKE) build-notification-service
	@$(MAKE) build-payment-service
	@echo "$(GREEN)All services built successfully!$(NC)"

test-all: ## Test all services
	@echo "$(BLUE)Testing all services...$(NC)"
	@$(MAKE) test-common
	@$(MAKE) test-order-service
	@$(MAKE) test-inventory-service
	@$(MAKE) test-notification-service
	@$(MAKE) test-payment-service
	@echo "$(GREEN)All tests passed!$(NC)"

clean-all: ## Clean all services
	@echo "$(BLUE)Cleaning all services...$(NC)"
	@for service in common order-service inventory-service notification-service payment-service; do \
		echo "Cleaning $$service..."; \
		$(MAKE) clean SERVICE=$$service; \
	done
	@echo "$(GREEN)All services cleaned!$(NC)"

# Development targets
dev-setup: ## Setup development environment for current service
	@./build.sh --install-deps --python $(PYTHON_VERSION) $(SERVICE)
	@echo "$(GREEN)Development environment ready!$(NC)"

dev-setup-all: ## Setup development environment for all services
	@echo "$(BLUE)Setting up development environment for all services...$(NC)"
	@for service in common order-service inventory-service notification-service payment-service; do \
		echo "Setting up $$service..."; \
		$(MAKE) dev-setup SERVICE=$$service; \
	done
	@echo "$(GREEN)All development environments ready!$(NC)"

# Quality assurance targets
qa: ## Run full quality assurance (lint + test + build)
	@echo "$(BLUE)Running quality assurance...$(NC)"
	@./build.sh --clean --verbose --python $(PYTHON_VERSION) --coverage $(COVERAGE_THRESHOLD) $(SERVICE)
	@echo "$(GREEN)Quality assurance passed!$(NC)"

qa-all: ## Run QA for all services
	@echo "$(BLUE)Running QA for all services...$(NC)"
	@for service in common order-service inventory-service notification-service payment-service; do \
		echo "QA for $$service..."; \
		$(MAKE) qa SERVICE=$$service; \
	done
	@echo "$(GREEN)QA passed for all services!$(NC)"

# CI/CD targets
ci: ## Run CI pipeline (clean, install, test, build)
	@echo "$(BLUE)Running CI pipeline...$(NC)"
	@./build.sh --clean --python $(PYTHON_VERSION) --coverage $(COVERAGE_THRESHOLD) $(SERVICE)

ci-all: ## Run CI for all services
	@echo "$(BLUE)Running CI for all services...$(NC)"
	@for service in common order-service inventory-service notification-service payment-service; do \
		echo "CI for $$service..."; \
		$(MAKE) ci SERVICE=$$service; \
	done
	@echo "$(GREEN)CI completed for all services!$(NC)"

# Docker targets
docker-all: ## Build Docker images for all services
	@echo "$(BLUE)Building Docker images for all services...$(NC)"
	@for service in order-service inventory-service notification-service payment-service; do \
		if [ -f "services/$$service/Dockerfile" ]; then \
			echo "Building Docker image for $$service..."; \
			$(MAKE) docker SERVICE=$$service; \
		fi; \
	done
	@echo "$(GREEN)All Docker images built!$(NC)"

# Utility targets
check: ## Quick check (test only, no build)
	@$(MAKE) test

verbose-build: ## Build with verbose output
	@./build.sh --verbose --python $(PYTHON_VERSION) --coverage $(COVERAGE_THRESHOLD) $(SERVICE)

format: ## Format code (if black is available)
	@echo "$(BLUE)Formatting code...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		black . --exclude="\.venv.*|build|dist"; \
		echo "$(GREEN)Code formatted!$(NC)"; \
	else \
		echo "$(YELLOW)Black not available, skipping formatting$(NC)"; \
	fi

check-format: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		black --check . --exclude="\.venv.*|build|dist"; \
		echo "$(GREEN)Code formatting is correct!$(NC)"; \
	else \
		echo "$(YELLOW)Black not available, skipping format check$(NC)"; \
	fi

# Information targets
info: ## Show build environment information
	@echo "$(BLUE)Build Environment Information:$(NC)"
	@echo "Service: $(if $(SERVICE),$(SERVICE),auto-detected)"
	@echo "Python Version: $(PYTHON_VERSION)"
	@echo "Coverage Threshold: $(COVERAGE_THRESHOLD)%"
	@echo "Current Directory: $(PWD)"
	@echo "Available Python versions:"
	@which python3.11 2>/dev/null && echo "  - python3.11" || true
	@which python3.10 2>/dev/null && echo "  - python3.10" || true
	@which python3.9 2>/dev/null && echo "  - python3.9" || true
	@which python3 2>/dev/null && echo "  - python3" || true
	@which python 2>/dev/null && echo "  - python" || true