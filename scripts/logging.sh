#!/bin/bash
# scripts/logging.sh
# Shared logging utilities for Cloud Native Order Processor
# Provides consistent logging across all deployment scripts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging levels
LOG_LEVEL_INFO=0
LOG_LEVEL_WARN=1
LOG_LEVEL_ERROR=2
LOG_LEVEL_DEBUG=3

# Default log level (can be overridden by setting LOG_LEVEL environment variable)
DEFAULT_LOG_LEVEL=${LOG_LEVEL:-$LOG_LEVEL_INFO}

# Timestamp format
TIMESTAMP_FORMAT="%Y-%m-%d %H:%M:%S"

# Logging functions
log_info() {
    if [[ $DEFAULT_LOG_LEVEL -le $LOG_LEVEL_INFO ]]; then
        local timestamp=$(date +"$TIMESTAMP_FORMAT")
        printf "${BLUE}[INFO]${NC} [%s] %s\n" "$timestamp" "$1"
    fi
}

log_success() {
    if [[ $DEFAULT_LOG_LEVEL -le $LOG_LEVEL_INFO ]]; then
        local timestamp=$(date +"$TIMESTAMP_FORMAT")
        printf "${GREEN}[SUCCESS]${NC} [%s] %s\n" "$timestamp" "$1"
    fi
}

log_warning() {
    if [[ $DEFAULT_LOG_LEVEL -le $LOG_LEVEL_WARN ]]; then
        local timestamp=$(date +"$TIMESTAMP_FORMAT")
        printf "${YELLOW}[WARNING]${NC} [%s] %s\n" "$timestamp" "$1"
    fi
}

log_error() {
    if [[ $DEFAULT_LOG_LEVEL -le $LOG_LEVEL_ERROR ]]; then
        local timestamp=$(date +"$TIMESTAMP_FORMAT")
        printf "${RED}[ERROR]${NC} [%s] %s\n" "$timestamp" "$1"
    fi
}

log_debug() {
    if [[ $DEFAULT_LOG_LEVEL -ge $LOG_LEVEL_DEBUG ]]; then
        local timestamp=$(date +"$TIMESTAMP_FORMAT")
        printf "${PURPLE}[DEBUG]${NC} [%s] %s\n" "$timestamp" "$1"
    fi
}

log_step() {
    if [[ $DEFAULT_LOG_LEVEL -le $LOG_LEVEL_INFO ]]; then
        local timestamp=$(date +"$TIMESTAMP_FORMAT")
        printf "${CYAN}[STEP]${NC} [%s] %s\n" "$timestamp" "$1"
    fi
}

# Section header logging
log_section() {
    local title="$1"
    local width=60
    local padding=$(( (width - ${#title} - 2) / 2 ))

    printf "\n"
    printf "${BLUE}%s${NC}\n" "$(printf '=%.0s' $(seq 1 $width))"
    printf "${BLUE}%s%s%s${NC}\n" "$(printf ' %.0s' $(seq 1 $padding))" "$title" "$(printf ' %.0s' $(seq 1 $padding))"
    printf "${BLUE}%s${NC}\n" "$(printf '=%.0s' $(seq 1 $width))"
    printf "\n"
}

# Progress indicator
log_progress() {
    local current="$1"
    local total="$2"
    local description="${3:-Progress}"
    local percentage=$(( (current * 100) / total ))
    local bar_width=30
    local filled=$(( (percentage * bar_width) / 100 ))
    local empty=$(( bar_width - filled ))

    printf "\r${CYAN}[%s]${NC} %s: [%s%s] %d%% (%d/%d)" \
        "$(date +"$TIMESTAMP_FORMAT")" \
        "$description" \
        "$(printf '█%.0s' $(seq 1 $filled))" \
        "$(printf '░%.0s' $(seq 1 $empty))" \
        "$percentage" \
        "$current" \
        "$total"

    if [[ $current -eq $total ]]; then
        printf "\n"
    fi
}

# Error handling with logging
log_and_exit() {
    local message="$1"
    local exit_code="${2:-1}"
    log_error "$message"
    exit "$exit_code"
}

# Success exit with logging
log_and_exit_success() {
    local message="$1"
    log_success "$message"
    exit 0
}

# Log command execution
log_command() {
    local command="$1"
    local description="${2:-Executing command}"

    log_debug "$description: $command"
    if [[ $DEFAULT_LOG_LEVEL -ge $LOG_LEVEL_DEBUG ]]; then
        printf "${PURPLE}[CMD]${NC} %s\n" "$command"
    fi
}

# Log command result
log_command_result() {
    local exit_code="$1"
    local command="$2"

    if [[ $exit_code -eq 0 ]]; then
        log_debug "Command succeeded: $command"
    else
        log_error "Command failed (exit code: $exit_code): $command"
    fi
}

# Export functions for use in other scripts
export -f log_info log_success log_warning log_error log_debug log_step
export -f log_section log_progress log_and_exit log_and_exit_success
export -f log_command log_command_result
