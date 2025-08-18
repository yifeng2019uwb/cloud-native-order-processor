#!/bin/bash

# Order Processor CLI Client
# Demonstrates how to interact with APIs from command line

set -e

# Configuration
API_BASE_URL="${API_BASE_URL:-http://localhost:30000}"
TOKEN_FILE="${HOME}/.order-processor-token"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if jq is installed
check_dependencies() {
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed. Please install jq first."
        exit 1
    fi
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed."
        exit 1
    fi
}

# Check and setup port forwarding if needed
setup_port_forwarding() {
    log_info "Checking if port forwarding is needed..."

    # Check if gateway is accessible
    if ! curl -s --max-time 5 "$API_BASE_URL/health" > /dev/null 2>&1; then
        log_warning "Gateway not accessible. Setting up port forwarding..."
        pkill -f "kubectl port-forward" || true
        kubectl port-forward svc/gateway 30000:8080 -n order-processor &
        kubectl port-forward svc/frontend 30004:80 -n order-processor &
        kubectl port-forward svc/user-service 30001:30001 -n order-processor &
        kubectl port-forward svc/inventory-service 30002:30002 -n order-processor &
        kubectl port-forward svc/order-service 30003:30003 -n order-processor &
        sleep 5
        log_success "Port forwarding set up"
    else
        log_success "Port forwarding already active"
    fi
}

# Load stored token
load_token() {
    if [[ -f "$TOKEN_FILE" ]]; then
        TOKEN=$(cat "$TOKEN_FILE")
        log_info "Loaded token from $TOKEN_FILE"
    else
        TOKEN=""
    fi
}

# Save token
save_token() {
    echo "$1" > "$TOKEN_FILE"
    chmod 600 "$TOKEN_FILE"
    log_success "Token saved to $TOKEN_FILE"
}

# Clear token
clear_token() {
    rm -f "$TOKEN_FILE"
    TOKEN=""
    log_success "Token cleared"
}

# Make authenticated request
api_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"

    local headers="-H 'Content-Type: application/json'"
    if [[ -n "$TOKEN" ]]; then
        headers="$headers -H 'Authorization: Bearer $TOKEN'"
    fi

    local curl_cmd="curl -s -X $method '$API_BASE_URL$endpoint' $headers"
    if [[ -n "$data" ]]; then
        curl_cmd="$curl_cmd -d '$data'"
    fi

    eval "$curl_cmd"
}

# Authentication commands
cmd_login() {
    local username="$1"
    local password="$2"

    if [[ -z "$username" || -z "$password" ]]; then
        log_error "Usage: $0 login <username> <password>"
        exit 1
    fi

    log_info "Logging in as $username..."

    local response=$(api_request POST "/api/v1/auth/login" "{\"username\":\"$username\",\"password\":\"$password\"}")

    if echo "$response" | jq -e '.success == true' > /dev/null; then
        local token=$(echo "$response" | jq -r '.access_token')
        save_token "$token"
        TOKEN="$token"

        local user=$(echo "$response" | jq -r '.user.username')
        log_success "Login successful! Welcome, $user"
    else
        local error=$(echo "$response" | jq -r '.message // .detail')
        log_error "Login failed: $error"
        exit 1
    fi
}

cmd_register() {
    local username="$1"
    local email="$2"
    local password="$3"
    local first_name="$4"
    local last_name="$5"

    if [[ -z "$username" || -z "$email" || -z "$password" || -z "$first_name" || -z "$last_name" ]]; then
        log_error "Usage: $0 register <username> <email> <password> <first_name> <last_name>"
        exit 1
    fi

    log_info "Registering user $username..."

    local data="{\"username\":\"$username\",\"email\":\"$email\",\"password\":\"$password\",\"first_name\":\"$first_name\",\"last_name\":\"$last_name\"}"
    local response=$(api_request POST "/api/v1/auth/register" "$data")

    if echo "$response" | jq -e '.success == true' > /dev/null; then
        local token=$(echo "$response" | jq -r '.access_token')
        save_token "$token"
        TOKEN="$token"

        log_success "Registration successful! Account created for $username"
    else
        local error=$(echo "$response" | jq -r '.message // .detail')
        log_error "Registration failed: $error"
        exit 1
    fi
}

cmd_logout() {
    if [[ -z "$TOKEN" ]]; then
        log_warning "No token to logout"
        return
    fi

    log_info "Logging out..."
    api_request POST "/api/v1/auth/logout" "{}" > /dev/null
    clear_token
    log_success "Logged out successfully"
}

cmd_profile() {
    if [[ -z "$TOKEN" ]]; then
        log_error "Not authenticated. Please login first."
        exit 1
    fi

    log_info "Fetching profile..."
    local response=$(api_request GET "/api/v1/auth/profile")

    if echo "$response" | jq -e '.username' > /dev/null; then
        echo "$response" | jq '.'
    else
        local error=$(echo "$response" | jq -r '.message // .detail')
        log_error "Failed to fetch profile: $error"
        exit 1
    fi
}

# Inventory commands
cmd_list_assets() {
    local limit="${1:-10}"

    log_info "Fetching assets (limit: $limit)..."
    local response=$(api_request GET "/api/v1/inventory/assets?limit=$limit")

    if echo "$response" | jq -e '.assets' > /dev/null; then
        echo "$response" | jq -r '.assets[] | "\(.asset_id): \(.name) - $\(.price_usd)"'
    else
        local error=$(echo "$response" | jq -r '.message // .detail')
        log_error "Failed to fetch assets: $error"
        exit 1
    fi
}

cmd_get_asset() {
    local asset_id="$1"

    if [[ -z "$asset_id" ]]; then
        log_error "Usage: $0 get-asset <asset_id>"
        exit 1
    fi

    log_info "Fetching asset $asset_id..."
    local response=$(api_request GET "/api/v1/inventory/assets/$asset_id")

    if echo "$response" | jq -e '.asset_id' > /dev/null; then
        echo "$response" | jq '.'
    else
        local error=$(echo "$response" | jq -r '.message // .detail')
        log_error "Failed to fetch asset: $error"
        exit 1
    fi
}

# Health check
cmd_health() {
    log_info "Checking service health..."
    local response=$(api_request GET "/health")

    if echo "$response" | jq -e '.status' > /dev/null; then
        echo "$response" | jq '.'
    else
        log_error "Health check failed"
        exit 1
    fi
}

# Show help
cmd_help() {
    cat << EOF
Order Processor CLI Client

Usage: $0 <command> [options]

Authentication:
  login <username> <password>     - Login with username and password
  register <username> <email> <password> <first_name> <last_name> - Register new user
  logout                          - Logout and clear token
  profile                         - Show current user profile

Inventory:
  list-assets [limit]             - List assets (default: 10)
  get-asset <asset_id>            - Get specific asset details

System:
  health                          - Check service health
  help                            - Show this help message

Environment Variables:
  API_BASE_URL                    - API base URL (default: http://localhost:30000)
  TOKEN_FILE                      - Token storage file (default: ~/.order-processor-token)

Examples:
  $0 login john_doe SecurePassword123!
  $0 register newuser user@example.com SecurePassword123! John Doe
  $0 list-assets 5
  $0 get-asset BTC
  $0 profile
  $0 logout

EOF
}

# Main script
main() {
    check_dependencies
    setup_port_forwarding
    load_token

    local command="$1"
    shift || true

    case "$command" in
        login)
            cmd_login "$@"
            ;;
        register)
            cmd_register "$@"
            ;;
        logout)
            cmd_logout
            ;;
        profile)
            cmd_profile
            ;;
        list-assets)
            cmd_list_assets "$@"
            ;;
        get-asset)
            cmd_get_asset "$@"
            ;;
        health)
            cmd_health
            ;;
        help|--help|-h)
            cmd_help
            ;;
        "")
            cmd_help
            ;;
        *)
            log_error "Unknown command: $command"
            log_info "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"