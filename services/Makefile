# Makefile for Python Microservices Build System
# This provides convenient targets for common build operations

.PHONY: help build test clean install lint format check-format docker build-test
.DEFAULT_GOAL := help

# Variables
SERVICE ?= $(shell basename $(CURDIR))
PYTHON_VERSION ?= 3.11
COVERAGE_THRESHOLD ?= 60

# Auto-detect service if we're in a service directory
ifeq ($(SERVICE),services)
    # We're in the services root, need to specify service
    SERVICE ?=
endif

# Colors for help output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

help: ## Show this help message
	@echo "$(BLUE)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)Usage examples:$(NC)"
	@echo "  make build                        # Build current service (auto-detected)"
	@echo "  make test                         # Test current service (auto-detected)"
	@echo "  make build-test                   # Build AND test current service"
	@echo ""
	@echo "  make build SERVICE=user_service   # Build specific service"
	@echo "  make test SERVICE=inventory_service # Test specific service"
	@echo "  make build-test SERVICE=common    # Build AND test specific service"
	@echo ""
	@echo "  make test-all                     # Test all services"
	@echo "  make build-all                    # Build all services"
	@echo "  make build-test-all               # Build AND test all services"
	@echo ""
	@if [ -n "$(SERVICE)" ]; then \
		echo "$(YELLOW)Current service: $(SERVICE)$(NC)"; \
	else \
		echo "$(YELLOW)No service specified. Use SERVICE=name or run from service directory$(NC)"; \
	fi

# ====================
# INDIVIDUAL SERVICE TARGETS
# ====================

build: ## Build current service (auto-detected) or specified service
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)Error: No service specified. Use SERVICE=name or run from service directory$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Building $(SERVICE) (build-only mode)...$(NC)"
	@./build.sh --build-only $(SERVICE)

test: ## Test current service (auto-detected) or specified service
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)Error: No service specified. Use SERVICE=name or run from service directory$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Running tests for $(SERVICE)...$(NC)"
	@./build.sh --test-only $(SERVICE)

build-test: ## Build AND test current service (auto-detected) or specified service
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)Error: No service specified. Use SERVICE=name or run from service directory$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Building AND testing $(SERVICE)...$(NC)"
	@./build.sh $(SERVICE)

# ====================
# ALL SERVICES TARGETS
# ====================

install-all: ## Install dependencies for all services
	@echo "$(BLUE)Installing dependencies for all services...$(NC)"
	@./build.sh --install-only --python $(PYTHON_VERSION)

test-all: ## Test all services
	@echo "$(BLUE)Testing all services...$(NC)"
	@./build.sh --test-only --python $(PYTHON_VERSION) --coverage $(COVERAGE_THRESHOLD)

build-all: ## Build all services
	@echo "$(BLUE)Building all services...$(NC)"
	@./build.sh --build-only --python $(PYTHON_VERSION)

build-test-all: ## Build AND test all services
	@echo "$(GREEN)Building AND testing all services...$(NC)"
	@./build.sh --python $(PYTHON_VERSION) --coverage $(COVERAGE_THRESHOLD)

# ====================
# UTILITY TARGETS
# ====================

clean: ## Clean build artifacts
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov*" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@find . -name "*.pyd" -delete 2>/dev/null || true
	@find . -name ".coverage" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleanup completed!$(NC)"

clean-venv: ## Clean virtual environments
	@echo "$(YELLOW)Cleaning virtual environments...$(NC)"
	@find . -type d -name ".venv*" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Virtual environments cleaned!$(NC)"

clean-all: clean clean-venv ## Clean everything (build artifacts + virtual environments)

# ====================
# DEVELOPMENT TARGETS
# ====================

dev-setup: ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@./build.sh --install-only --python $(PYTHON_VERSION)
	@echo "$(GREEN)Development environment ready!$(NC)"

dev-test: ## Quick test for development (current service only)
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)Error: No service specified. Use SERVICE=name or run from service directory$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Quick test for $(SERVICE)...$(NC)"
	@./build.sh --test-only $(SERVICE) --coverage $(COVERAGE_THRESHOLD)