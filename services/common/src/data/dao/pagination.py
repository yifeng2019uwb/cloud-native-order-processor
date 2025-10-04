"""
Global Pagination Models for All Services

This file contains pagination models and constants that will be shared across all services.
"""

# ==================== PAGINATION CONSTANTS ====================

class PaginationFields:
    """Pagination field names - shared across all DAOs"""
    LAST_EVALUATED_KEY = "last_evaluated_key"


# ==================== FUTURE PAGINATION MODELS ====================
# Planned Models:
# - PaginationRequest (limit, offset, cursor-based)
# - PaginationResponse (total_count, has_next, has_previous)
# - CursorPagination (for better performance with large datasets)
#
# Services to be updated:
# - user_service
# - inventory_service
# - order_service
#
# Implementation Notes:
# - Will be implemented in common package for consistency
# - Will support both offset-based and cursor-based pagination
# - Will include metadata for pagination state
# - Will be consistent with industry standards
#
# Status: Planned for future implementation when all services are ready for pagination standardization.