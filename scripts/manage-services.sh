#!/bin/bash

# Service Management Script for Cloud Native Order Processor
# Usage: ./manage-services.sh [start|stop|restart|status] [all|frontend|user-service|inventory-service]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DIR="frontend"
USER_SERVICE_DIR="services/user-service"
INVENTORY_SERVICE_DIR="services/inventory-service"
FRONTEND_PORT=3000
USER_SERVICE_PORT=8000
INVENTORY_SERVICE_PORT=8001

# Log files
LOG_DIR="logs"
FRONTEND_LOG="$LOG_DIR/frontend.log"
USER_SERVICE_LOG="$LOG_DIR/user-service.log"
INVENTORY_SERVICE_LOG="$LOG_DIR/inventory-service.log"

# PID files
FRONTEND_PID="$LOG_DIR/frontend.pid"
USER_SERVICE_PID="$LOG_DIR/user-service.pid"
INVENTORY_SERVICE_PID="$LOG_DIR/inventory-service.pid"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a service is running
is_service_running() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID file exists but process is dead
            rm -f "$pid_file"
        fi
    fi
    return 1
}

# Function to get service status
get_service_status() {
    local pid_file=$1
    local service_name=$2
    local port=$3

    if is_service_running "$pid_file" "$service_name"; then
        local pid=$(cat "$pid_file")
        echo -e "${GREEN}✓${NC} $service_name is running (PID: $pid, Port: $port)"
        return 0
    else
        echo -e "${RED}✗${NC} $service_name is not running"
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend..."

    if is_service_running "$FRONTEND_PID" "Frontend"; then
        print_warning "Frontend is already running"
        return 0
    fi

    cd "$FRONTEND_DIR" || {
        print_error "Failed to change to frontend directory"
        return 1
    }

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi

    # Start frontend in background
    npm run dev > "../$FRONTEND_LOG" 2>&1 &
    local pid=$!
    echo $pid > "../$FRONTEND_PID"

    cd ..

    # Wait a moment for the service to start
    sleep 3

    if is_service_running "$FRONTEND_PID" "Frontend"; then
        print_success "Frontend started successfully (PID: $pid)"
        print_status "Frontend URL: http://localhost:$FRONTEND_PORT (or next available port)"
    else
        print_error "Failed to start frontend"
        return 1
    fi
}

# Function to start user service
start_user_service() {
    print_status "Starting user service..."

    if is_service_running "$USER_SERVICE_PID" "User Service"; then
        print_warning "User service is already running"
        return 0
    fi

    cd "$USER_SERVICE_DIR" || {
        print_error "Failed to change to user service directory"
        return 1
    }

    # Activate virtual environment
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "../.venv" ]; then
        source ../.venv/bin/activate
    else
        print_error "Virtual environment not found"
        return 1
    fi

    # Start user service in background
    python -m uvicorn src.main:app --host 0.0.0.0 --port $USER_SERVICE_PORT --reload > "../../$USER_SERVICE_LOG" 2>&1 &
    local pid=$!
    echo $pid > "../../$USER_SERVICE_PID"

    cd ../..

    # Wait a moment for the service to start
    sleep 3

    if is_service_running "$USER_SERVICE_PID" "User Service"; then
        print_success "User service started successfully (PID: $pid)"
        print_status "User Service URL: http://localhost:$USER_SERVICE_PORT"
    else
        print_error "Failed to start user service"
        return 1
    fi
}

# Function to start inventory service
start_inventory_service() {
    print_status "Starting inventory service..."

    if is_service_running "$INVENTORY_SERVICE_PID" "Inventory Service"; then
        print_warning "Inventory service is already running"
        return 0
    fi

    cd "$INVENTORY_SERVICE_DIR" || {
        print_error "Failed to change to inventory service directory"
        return 1
    }

    # Activate virtual environment
    if [ -d ".venv-inventory-service" ]; then
        source .venv-inventory-service/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        print_error "Virtual environment not found"
        return 1
    fi

    # Start inventory service in background
    python -m uvicorn src.main:app --host 0.0.0.0 --port $INVENTORY_SERVICE_PORT --reload > "../../$INVENTORY_SERVICE_LOG" 2>&1 &
    local pid=$!
    echo $pid > "../../$INVENTORY_SERVICE_PID"

    cd ../..

    # Wait a moment for the service to start
    sleep 3

    if is_service_running "$INVENTORY_SERVICE_PID" "Inventory Service"; then
        print_success "Inventory service started successfully (PID: $pid)"
        print_status "Inventory Service URL: http://localhost:$INVENTORY_SERVICE_PORT"
    else
        print_error "Failed to start inventory service"
        return 1
    fi
}

# Function to stop a service
stop_service() {
    local pid_file=$1
    local service_name=$2

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            print_status "Stopping $service_name (PID: $pid)..."
            kill "$pid"

            # Wait for the process to terminate
            local count=0
            while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done

            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                print_warning "Force killing $service_name..."
                kill -9 "$pid"
            fi

            rm -f "$pid_file"
            print_success "$service_name stopped"
        else
            print_warning "$service_name was not running"
            rm -f "$pid_file"
        fi
    else
        print_warning "$service_name was not running"
    fi
}

# Function to stop frontend
stop_frontend() {
    stop_service "$FRONTEND_PID" "Frontend"
}

# Function to stop user service
stop_user_service() {
    stop_service "$USER_SERVICE_PID" "User Service"
}

# Function to stop inventory service
stop_inventory_service() {
    stop_service "$INVENTORY_SERVICE_PID" "Inventory Service"
}

# Function to start all services
start_all() {
    print_status "Starting all services..."

    # Start services in order (backend first, then frontend)
    start_user_service
    start_inventory_service
    start_frontend

    print_success "All services started!"
    print_status "Access the application at: http://localhost:$FRONTEND_PORT"
}

# Function to stop all services
stop_all() {
    print_status "Stopping all services..."

    stop_frontend
    stop_user_service
    stop_inventory_service

    print_success "All services stopped!"
}

# Function to restart a service
restart_service() {
    local service=$1
    print_status "Restarting $service..."

    case $service in
        "frontend")
            stop_frontend
            start_frontend
            ;;
        "user-service")
            stop_user_service
            start_user_service
            ;;
        "inventory-service")
            stop_inventory_service
            start_inventory_service
            ;;
        "all")
            stop_all
            start_all
            ;;
        *)
            print_error "Unknown service: $service"
            exit 1
            ;;
    esac
}

# Function to show status of all services
show_status() {
    print_status "Service Status:"
    echo "=================="

    local all_running=true

    if ! get_service_status "$FRONTEND_PID" "Frontend" "$FRONTEND_PORT"; then
        all_running=false
    fi

    if ! get_service_status "$USER_SERVICE_PID" "User Service" "$USER_SERVICE_PORT"; then
        all_running=false
    fi

    if ! get_service_status "$INVENTORY_SERVICE_PID" "Inventory Service" "$INVENTORY_SERVICE_PORT"; then
        all_running=false
    fi

    echo ""
    if [ "$all_running" = true ]; then
        print_success "All services are running!"
        print_status "Access the application at: http://localhost:$FRONTEND_PORT"
    else
        print_warning "Some services are not running"
    fi
}

# Function to show logs
show_logs() {
    local service=$1

    case $service in
        "frontend")
            if [ -f "$FRONTEND_LOG" ]; then
                tail -f "$FRONTEND_LOG"
            else
                print_error "Frontend log file not found"
            fi
            ;;
        "user-service")
            if [ -f "$USER_SERVICE_LOG" ]; then
                tail -f "$USER_SERVICE_LOG"
            else
                print_error "User service log file not found"
            fi
            ;;
        "inventory-service")
            if [ -f "$INVENTORY_SERVICE_LOG" ]; then
                tail -f "$INVENTORY_SERVICE_LOG"
            else
                print_error "Inventory service log file not found"
            fi
            ;;
        *)
            print_error "Unknown service: $service"
            exit 1
            ;;
    esac
}

# Function to show help
show_help() {
    echo "Service Management Script for Cloud Native Order Processor"
    echo ""
    echo "Usage: $0 [COMMAND] [SERVICE]"
    echo ""
    echo "Commands:"
    echo "  start     Start a service or all services"
    echo "  stop      Stop a service or all services"
    echo "  restart   Restart a service or all services"
    echo "  status    Show status of all services"
    echo "  logs      Show logs for a specific service"
    echo "  help      Show this help message"
    echo ""
    echo "Services:"
    echo "  all              All services (frontend, user-service, inventory-service)"
    echo "  frontend         React frontend application"
    echo "  user-service     FastAPI user authentication service"
    echo "  inventory-service FastAPI inventory management service"
    echo ""
    echo "Examples:"
    echo "  $0 start all                    # Start all services"
    echo "  $0 stop frontend                # Stop frontend only"
    echo "  $0 restart user-service         # Restart user service"
    echo "  $0 status                       # Show status of all services"
    echo "  $0 logs inventory-service       # Show inventory service logs"
    echo ""
    echo "Log files are stored in: $LOG_DIR"
}

# Main script logic
case "${1:-help}" in
    "start")
        case "${2:-all}" in
            "all")
                start_all
                ;;
            "frontend")
                start_frontend
                ;;
            "user-service")
                start_user_service
                ;;
            "inventory-service")
                start_inventory_service
                ;;
            *)
                print_error "Unknown service: $2"
                show_help
                exit 1
                ;;
        esac
        ;;
    "stop")
        case "${2:-all}" in
            "all")
                stop_all
                ;;
            "frontend")
                stop_frontend
                ;;
            "user-service")
                stop_user_service
                ;;
            "inventory-service")
                stop_inventory_service
                ;;
            *)
                print_error "Unknown service: $2"
                show_help
                exit 1
                ;;
        esac
        ;;
    "restart")
        restart_service "${2:-all}"
        ;;
    "status")
        show_status
        ;;
    "logs")
        if [ -z "$2" ]; then
            print_error "Please specify a service for logs"
            show_help
            exit 1
        fi
        show_logs "$2"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac