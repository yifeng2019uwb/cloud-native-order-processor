"""
Constants for database mock operations in unit tests.
This centralizes the mock method names used across all DAO unit tests.
"""


class MockDatabaseMethods:
    """Constants for PynamoDB mock method names"""

    # PynamoDB Model methods
    SAVE = 'save'
    GET = 'get'
    QUERY = 'query'
    SCAN = 'scan'
    DELETE = 'delete'
    UPDATE = 'update'

    # PynamoDB Query methods
    QUERY_INDEX = 'query_index'
    SCAN_INDEX = 'scan_index'

    # PynamoDB Batch methods
    BATCH_GET = 'batch_get'
    BATCH_WRITE = 'batch_write'

    # PynamoDB Exception classes
    DOES_NOT_EXIST = 'DoesNotExist'
    QUERY_ERROR = 'QueryError'
    SCAN_ERROR = 'ScanError'
    PUT_ERROR = 'PutError'
    DELETE_ERROR = 'DeleteError'
    UPDATE_ERROR = 'UpdateError'


class MockDatabaseFields:
    """Constants for mock database field names"""

    # Common DynamoDB fields
    PK = 'Pk'
    SK = 'Sk'
    GSI1_PK = 'GSI1PK'
    GSI1_SK = 'GSI1SK'

    # Pagination fields
    LAST_EVALUATED_KEY = 'last_evaluated_key'
    EXCLUSIVE_START_KEY = 'exclusive_start_key'

    # Response fields
    ITEMS = 'Items'
    COUNT = 'Count'
    SCANNED_COUNT = 'ScannedCount'
