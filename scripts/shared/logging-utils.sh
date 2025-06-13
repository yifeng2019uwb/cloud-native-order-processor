# #!/bin/bash
# # File: scripts/shared/logging-utils.sh
# # Logging and output utilities
# # Colored output with terminal detection
# # Multiple log levels (ERROR, WARN, INFO, DEBUG)
# # Special formatting (success, failure, progress, sections)
# # Command execution with optional output capture
# # Progress spinner for long-running operations

# set -euo pipefail

# # Color codes for output
# declare -r RED='\033[0;31m'
# declare -r GREEN='\033[0;32m'
# declare -r YELLOW='\033[1;33m'
# declare -r BLUE='\033[0;34m'
# declare -r PURPLE='\033[0;35m'
# declare -r CYAN='\033[0;36m'
# declare -r WHITE='\033[1;37m'
# declare -r NC='\033[0m' # No Color

# # Log levels
# declare -r LOG_LEVEL_ERROR=0
# declare -r LOG_LEVEL_WARN=1
# declare -r LOG_LEVEL_INFO=2
# declare -r LOG_LEVEL_DEBUG=3

# # Set default log level
# LOG_LEVEL="${LOG_LEVEL:-INFO}"

# # Convert log level string to number
# get_log_level_number() {
#         case "$(echo "${LOG_LEVEL}" | tr '[:lower:]' '[:upper:]')" in
#         ERROR) echo ${LOG_LEVEL_ERROR} ;;
#         WARN|WARNING) echo ${LOG_LEVEL_WARN} ;;
#         INFO) echo ${LOG_LEVEL_INFO} ;;
#         DEBUG) echo ${LOG_LEVEL_DEBUG} ;;
#         *) echo ${LOG_LEVEL_INFO} ;;
#     esac
# }

# # Check if colors should be used
# use_colors() {
#     if [[ "${COLOR_OUTPUT:-true}" == "false" ]]; then
#         return 1
#     fi

#     if [[ ! -t 1 ]]; then
#         # Not a terminal
#         return 1
#     fi

#     return 0
# }

# # Get timestamp
# get_timestamp() {
#     date '+%Y-%m-%d %H:%M:%S'
# }

# # Generic log function
# log_message() {
#     local level="${1}"
#     local level_num="${2}"
#     local color="${3}"
#     local message="${4}"

#     local current_level_num
#     current_level_num=$(get_log_level_number)

#     # Only log if current level allows this message
#     if [[ ${level_num} -le ${current_level_num} ]]; then
#         local timestamp
#         timestamp=$(get_timestamp)

#         if use_colors; then
#             echo -e "${color}[${timestamp}] ${level}: ${message}${NC}" >&2
#         else
#             echo "[${timestamp}] ${level}: ${message}" >&2
#         fi
#     fi
# }

# # Specific log level functions
# log_error() {
#     log_message "ERROR" ${LOG_LEVEL_ERROR} "${RED}" "$*"
# }

# log_warn() {
#     log_message "WARN" ${LOG_LEVEL_WARN} "${YELLOW}" "$*"
# }

# log_info() {
#     log_message "INFO" ${LOG_LEVEL_INFO} "${GREEN}" "$*"
# }

# log_debug() {
#     log_message "DEBUG" ${LOG_LEVEL_DEBUG} "${BLUE}" "$*"
# }

# # Special formatting functions
# log_success() {
#     if use_colors; then
#         echo -e "${GREEN}✓ $*${NC}"
#     else
#         echo "✓ $*"
#     fi
# }

# log_failure() {
#     if use_colors; then
#         echo -e "${RED}✗ $*${NC}"
#     else
#         echo "✗ $*"
#     fi
# }

# log_warning() {
#     if use_colors; then
#         echo -e "${YELLOW}⚠ $*${NC}"
#     else
#         echo "⚠ $*"
#     fi
# }

# log_progress() {
#     local message="$1"
#     local current="${2:-}"
#     local total="${3:-}"

#     if [[ -n "${current}" && -n "${total}" ]]; then
#         local percentage
#         percentage=$(( (current * 100) / total ))
#         message="${message} (${current}/${total} - ${percentage}%)"
#     fi

#     if use_colors; then
#         echo -e "${CYAN}⏳ ${message}${NC}"
#     else
#         echo "⏳ ${message}"
#     fi
# }

# # Section headers
# log_section() {
#     local title="$1"
#     local width=80
#     local padding=$(( (width - ${#title} - 2) / 2 ))

#     if use_colors; then
#         echo -e "\n${WHITE}$(printf '%*s' ${width} '' | tr ' ' '=')${NC}"
#         echo -e "${WHITE}$(printf '%*s' ${padding} '')${title}$(printf '%*s' ${padding} '')${NC}"
#         echo -e "${WHITE}$(printf '%*s' ${width} '' | tr ' ' '=')${NC}\n"
#     else
#         echo ""
#         printf '%*s\n' ${width} '' | tr ' ' '='
#         printf '%*s%s%*s\n' ${padding} '' "${title}" ${padding} ''
#         printf '%*s\n' ${width} '' | tr ' ' '='
#         echo ""
#     fi
# }

# # Subsection headers
# log_subsection() {
#     local title="$1"

#     if use_colors; then
#         echo -e "\n${PURPLE}--- ${title} ---${NC}\n"
#     else
#         echo ""
#         echo "--- ${title} ---"
#         echo ""
#     fi
# }

# # Progress spinner
# show_spinner() {
#     local pid=$1
#     local message="${2:-Processing...}"
#     local delay=0.1
#     local spinstr='|/-\'

#     if [[ ! -t 1 ]]; then
#         # Not a terminal, just wait
#         wait ${pid}
#         return $?
#     fi

#     while kill -0 ${pid} 2>/dev/null; do
#         local temp=${spinstr#?}
#         if use_colors; then
#             printf "\r${CYAN}%c ${message}${NC}" "${spinstr}"
#         else
#             printf "\r%c ${message}" "${spinstr}"
#         fi
#         local spinstr=${temp}${spinstr%"$temp"}
#         sleep ${delay}
#     done

#     printf "\r%*s\r" ${#message} ""
#     wait ${pid}
#     return $?
# }

# # Command execution with logging
# run_command() {
#     local command="$*"

#     log_debug "Executing command: ${command}"

#     if [[ "${TEST_VERBOSE:-false}" == "true" ]]; then
#         # Show command output in verbose mode
#         if eval "${command}"; then
#             log_debug "Command completed successfully: ${command}"
#             return 0
#         else
#             local exit_code=$?
#             log_error "Command failed with exit code ${exit_code}: ${command}"
#             return ${exit_code}
#         fi
#     else
#         # Capture output and only show on error
#         local output
#         local exit_code

#         if output=$(eval "${command}" 2>&1); then
#             log_debug "Command completed successfully: ${command}"
#             return 0
#         else
#             exit_code=$?
#             log_error "Command failed with exit code ${exit_code}: ${command}"
#             log_error "Command output:"
#             echo "${output}" >&2
#             return ${exit_code}
#         fi
#     fi
# }

# # Initialize logging (call this in main scripts)
# init_logging() {
#     # Set log level from environment
#     if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
#         LOG_LEVEL="DEBUG"
#     elif [[ "${TEST_VERBOSE:-false}" == "true" ]]; then
#         LOG_LEVEL="INFO"
#     fi

#     export LOG_LEVEL

#     log_debug "Logging initialized with level: ${LOG_LEVEL}"
# }

# # Export functions for use in other scripts
# export -f log_error log_warn log_info log_debug
# export -f log_success log_failure log_warning log_progress
# export -f log_section log_subsection
# export -f show_spinner run_command init_logging
