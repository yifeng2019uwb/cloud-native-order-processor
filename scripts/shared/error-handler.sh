# #!/bin/bash
# # File: scripts/shared/error-handler.sh
# # Error handling and rollback utilities
# # Automatic error trapping with stack traces
# # Cleanup and rollback function registration
# # Safe command execution with retry logic
# # Environment-aware rollback (terraform destroy, k8s cleanup)
# # Graceful interrupt handling (Ctrl+C)

# set -euo pipefail

# # Global variables for error handling (compatible with older Bash)
# ERROR_OCCURRED=false
# CLEANUP_FUNCTIONS=()
# ROLLBACK_FUNCTIONS=()

# # Error handling setup
# setup_error_handling() {
#     # Set up trap to handle errors and cleanup
#     trap 'handle_error ${LINENO} "${BASH_COMMAND}"' ERR
#     trap 'handle_exit' EXIT
#     trap 'handle_interrupt' INT TERM

#     log_debug "Error handling initialized"
# }

# # Handle script errors
# handle_error() {
#     local line_number="${1}"
#     local command="${2}"
#     local exit_code=$?

#     ERROR_OCCURRED=true

#     log_error "Script failed at line ${line_number}: ${command}"
#     log_error "Exit code: ${exit_code}"

#     # Show stack trace if debug mode is enabled
#     if [[ "${DEBUG_MODE:-false}" == "true" ]]; then
#         show_stack_trace
#     fi

#     # Execute rollback functions if any are registered
#     execute_rollback_functions

#     # Exit with error code
#     exit ${exit_code}
# }

# # Handle script exit (success or failure)
# handle_exit() {
#     local exit_code=$?

#     if [[ "${ERROR_OCCURRED}" == "true" ]]; then
#         log_error "Script exiting due to error"
#     else
#         log_debug "Script exiting normally"
#     fi

#     # Always execute cleanup functions
#     execute_cleanup_functions

#     exit ${exit_code}
# }

# # Handle interruption (Ctrl+C, etc.)
# handle_interrupt() {
#     log_warn "Script interrupted by user"
#     ERROR_OCCURRED=true

#     # Execute rollback and cleanup
#     execute_rollback_functions
#     execute_cleanup_functions

#     exit 130 # Standard exit code for script terminated by Control-C
# }

# # Show stack trace for debugging
# show_stack_trace() {
#     log_debug "=== Stack Trace ==="
#     local frame=0
#     while caller $frame; do
#         ((frame++))
#     done
#     log_debug "=================="
# }

# # Register cleanup function
# register_cleanup_function() {
#     local cleanup_function="${1}"

#     if [[ -z "${cleanup_function}" ]]; then
#         log_error "No cleanup function provided to register_cleanup_function"
#         return 1
#     fi

#     CLEANUP_FUNCTIONS+=("${cleanup_function}")
#     log_debug "Registered cleanup function: ${cleanup_function}"
# }

# # Register rollback function
# register_rollback_function() {
#     local rollback_function="${1}"

#     if [[ -z "${rollback_function}" ]]; then
#         log_error "No rollback function provided to register_rollback_function"
#         return 1
#     fi

#     ROLLBACK_FUNCTIONS+=("${rollback_function}")
#     log_debug "Registered rollback function: ${rollback_function}"
# }

# # Execute cleanup functions
# execute_cleanup_functions() {
#     if [[ ${#CLEANUP_FUNCTIONS[@]} -eq 0 ]]; then
#         log_debug "No cleanup functions to execute"
#         return 0
#     fi

#     log_info "Executing cleanup functions..."

#     for cleanup_function in "${CLEANUP_FUNCTIONS[@]}"; do
#         log_debug "Executing cleanup function: ${cleanup_function}"

#         # Execute cleanup function and continue even if it fails
#         if ! ${cleanup_function}; then
#             log_warn "Cleanup function failed: ${cleanup_function}"
#         else
#             log_debug "Cleanup function completed: ${cleanup_function}"
#         fi
#     done

#     log_info "Cleanup functions completed"
# }

# # Execute rollback functions
# execute_rollback_functions() {
#     if [[ ${#ROLLBACK_FUNCTIONS[@]} -eq 0 ]]; then
#         log_debug "No rollback functions to execute"
#         return 0
#     fi

#     log_warn "Executing rollback functions due to error..."

#     # Execute rollback functions in reverse order
#     local i
#     for (( i=${#ROLLBACK_FUNCTIONS[@]}-1; i>=0; i-- )); do
#         local rollback_function="${ROLLBACK_FUNCTIONS[i]}"
#         log_debug "Executing rollback function: ${rollback_function}"

#         # Execute rollback function and continue even if it fails
#         if ! ${rollback_function}; then
#             log_warn "Rollback function failed: ${rollback_function}"
#         else
#             log_debug "Rollback function completed: ${rollback_function}"
#         fi
#     done

#     log_warn "Rollback functions completed"
# }

# # Safe command execution with retry
# safe_execute() {
#     local command="$1"
#     local max_retries="${2:-${TEST_RETRY_COUNT:-3}}"
#     local retry_delay="${3:-${TEST_RETRY_DELAY:-5}}"
#     local description="${4:-command}"

#     local attempt=1

#     while [[ ${attempt} -le ${max_retries} ]]; do
#         log_debug "Executing ${description} (attempt ${attempt}/${max_retries}): ${command}"

#         if eval "${command}"; then
#             log_debug "${description} completed successfully on attempt ${attempt}"
#             return 0
#         else
#             local exit_code=$?

#             if [[ ${attempt} -eq ${max_retries} ]]; then
#                 log_error "${description} failed after ${max_retries} attempts"
#                 return ${exit_code}
#             else
#                 log_warn "${description} failed on attempt ${attempt}, retrying in ${retry_delay} seconds..."
#                 sleep "${retry_delay}"
#                 ((attempt++))
#             fi
#         fi
#     done
# }

# # Check if rollback is needed
# should_rollback() {
#     local environment="${ENVIRONMENT:-}"

#     # Always rollback in CI environment
#     if [[ "${environment}" == "ci" ]]; then
#         return 0
#     fi

#     # Check if auto-cleanup is enabled
#     if [[ "${AUTO_CLEANUP_ENABLED:-false}" == "true" ]]; then
#         return 0
#     fi

#     # Check if infrastructure test cleanup is enabled
#     if [[ "${INFRA_TEST_CLEANUP:-true}" == "true" ]]; then
#         return 0
#     fi

#     # Don't rollback in local development by default
#     return 1
# }

# # Terraform rollback function
# rollback_terraform() {
#     log_warn "Rolling back Terraform infrastructure..."

#     local terraform_dir="${PROJECT_ROOT}/terraform"

#     if [[ ! -d "${terraform_dir}" ]]; then
#         log_warn "Terraform directory not found, skipping Terraform rollback"
#         return 0
#     fi

#     pushd "${terraform_dir}" >/dev/null

#     # Check if there's anything to destroy
#     if ! terraform state list >/dev/null 2>&1; then
#         log_info "No Terraform state found, nothing to rollback"
#         popd >/dev/null
#         return 0
#     fi

#     # Destroy infrastructure
#     local destroy_command="terraform destroy"

#     if [[ "${TERRAFORM_DESTROY_AUTO_APPROVE:-false}" == "true" ]]; then
#         destroy_command="${destroy_command} -auto-approve"
#     fi

#     if ! safe_execute "${destroy_command}" 3 10 "Terraform destroy"; then
#         log_error "Failed to destroy Terraform infrastructure"
#         popd >/dev/null
#         return 1
#     fi

#     popd >/dev/null
#     log_info "Terraform infrastructure rolled back successfully"
#     return 0
# }

# # Kubernetes rollback function
# rollback_kubernetes() {
#     log_warn "Rolling back Kubernetes resources..."

#     local namespace="${K8S_NAMESPACE_PREFIX:-order-processor}-${ENVIRONMENT:-dev}"

#     # Check if kubectl is available
#     if ! command -v kubectl >/dev/null 2>&1; then
#         log_warn "kubectl not available, skipping Kubernetes rollback"
#         return 0
#     fi

#     # Check if namespace exists
#     if ! kubectl get namespace "${namespace}" >/dev/null 2>&1; then
#         log_info "Kubernetes namespace '${namespace}' does not exist, nothing to rollback"
#         return 0
#     fi

#     # Delete namespace and all resources in it
#     if ! safe_execute "kubectl delete namespace ${namespace}" 3 10 "Kubernetes namespace deletion"; then
#         log_error "Failed to delete Kubernetes namespace: ${namespace}"
#         return 1
#     fi

#     log_info "Kubernetes resources rolled back successfully"
#     return 0
# }

# # Export functions for use in other scripts
# export -f setup_error_handling
# export -f register_cleanup_function register_rollback_function
# export -f safe_execute should_rollback
# export -f rollback_terraform rollback_kubernetes
