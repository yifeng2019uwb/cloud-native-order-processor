"""
Asset Transaction Controller
Path: services/order_service/src/controllers/asset_transaction.py

Handles asset transaction history endpoints
- GET /assets/{asset_id}/transactions - Get asset transaction history
"""
from datetime import datetime, timezone
from typing import Union
from fastapi import APIRouter, Depends, status, Request
from api_models.asset import (
    GetAssetTransactionsResponse,
    AssetTransactionData
)
from api_models.shared.common import ErrorResponse
from common.data.dao.asset.asset_transaction_dao import AssetTransactionDAO
from common.data.dao.inventory.asset_dao import AssetDAO
from common.data.dao.user.user_dao import UserDAO
from common.exceptions import (
    CNOPDatabaseOperationException,
    CNOPEntityNotFoundException
)
from common.exceptions.shared_exceptions import CNOPInternalServerException
from common.shared.logging import BaseLogger, Loggers, LogActions, LogFields, LogExtraDefaults
from common.shared.constants.http_status import HTTPStatus
from common.shared.constants.api_responses import APIResponseDescriptions
from api_info_enum import ApiTags, ApiResponseKeys, API_ASSET_TRANSACTIONS
from constants import MSG_SUCCESS_ASSET_TRANSACTIONS_RETRIEVED, MSG_ERROR_ASSET_NOT_FOUND
from common.shared.constants.error_messages import ErrorMessages
from controllers.dependencies import (
    get_current_user, get_asset_transaction_dao_dependency,
    get_asset_dao_dependency, get_user_dao_dependency,
    get_request_id_from_request
)
from validation.business_validators import validate_order_history_business_rules

# Initialize our standardized logger
logger = BaseLogger(Loggers.ORDER)
router = APIRouter(tags=[ApiTags.ASSET_TRANSACTIONS.value])


@router.get(
    API_ASSET_TRANSACTIONS,
    response_model=Union[GetAssetTransactionsResponse, ErrorResponse],
    responses={
        HTTPStatus.OK: {
            ApiResponseKeys.DESCRIPTION.value: MSG_SUCCESS_ASSET_TRANSACTIONS_RETRIEVED,
            ApiResponseKeys.MODEL.value: GetAssetTransactionsResponse
        },
        HTTPStatus.UNAUTHORIZED: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_AUTHENTICATION_FAILED,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.NOT_FOUND: {
            ApiResponseKeys.DESCRIPTION.value: MSG_ERROR_ASSET_NOT_FOUND,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_VALIDATION,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.SERVICE_UNAVAILABLE: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_SERVICE_UNAVAILABLE,
            ApiResponseKeys.MODEL.value: ErrorResponse
        }
    }
)
def get_asset_transactions(
    asset_id: str,
    request: Request,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    asset_transaction_dao: AssetTransactionDAO = Depends(get_asset_transaction_dao_dependency),
    asset_dao: AssetDAO = Depends(get_asset_dao_dependency),
    user_dao: UserDAO = Depends(get_user_dao_dependency)
) -> GetAssetTransactionsResponse:
    """
    Get asset transaction history for the authenticated user
    """
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    # Log request
    logger.info(
        action=LogActions.REQUEST_START,
        message=f"Asset transactions request from {request.client.host if request.client else 'unknown'}",
        user=current_user["username"],
        request_id=request_id,
        extra={
            LogFields.ASSET_ID: asset_id,
            LogFields.LIMIT: limit,
            LogFields.OFFSET: offset,
            LogFields.USER_AGENT: request.headers.get(LogFields.USER_AGENT, LogExtraDefaults.UNKNOWN_USER_AGENT) if request else LogExtraDefaults.UNKNOWN_USER_AGENT,
            LogFields.TIMESTAMP: datetime.now(timezone.utc).isoformat()
        }
    )

    try:
        # Business validation (Layer 2)
        validate_order_history_business_rules(
            asset_id=asset_id,
            username=current_user["username"],
            asset_dao=asset_dao,
            user_dao=user_dao
        )

        # Get asset transactions for user
        asset_transactions = asset_transaction_dao.get_user_asset_transactions(
            current_user["username"],
            asset_id,
            limit=limit
        )

        # Convert to API response format
        transaction_data_list = []
        for transaction in asset_transactions:
            transaction_data = AssetTransactionData(
                asset_id=transaction.asset_id,
                transaction_type=transaction.transaction_type,
                quantity=transaction.quantity,
                price=transaction.price,
                status=transaction.status,
                timestamp=transaction.created_at
            )
            transaction_data_list.append(transaction_data)

        # Determine if there are more transactions
        has_more = len(transaction_data_list) == limit

        logger.info(
            action=LogActions.REQUEST_END,
            message=f"Asset transactions retrieved successfully: asset={asset_id}, count={len(transaction_data_list)}, has_more={has_more}",
            user=current_user['username'],
            request_id=request_id
        )

        return GetAssetTransactionsResponse(
            success=True,
            message=MSG_SUCCESS_ASSET_TRANSACTIONS_RETRIEVED,
            data=transaction_data_list,
            has_more=has_more,
            timestamp=datetime.utcnow()
        )

    except CNOPEntityNotFoundException:
        logger.info(
            action=LogActions.REQUEST_END,
            message=f"No asset transactions found: asset={asset_id}",
            user=current_user['username'],
            request_id=request_id
        )
        # Return empty list instead of error for no transactions
        return GetAssetTransactionsResponse(
            success=True,
            message="No asset transactions found",
            data=[],
            has_more=False,
            timestamp=datetime.utcnow()
        )
    except CNOPDatabaseOperationException as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Database operation failed for asset transactions: asset={asset_id}, error={str(e)}",
            user=current_user['username'],
            request_id=request_id
        )
        raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)
    except Exception as e:
        logger.error(
            action=LogActions.ERROR,
            message=f"Unexpected error during asset transactions retrieval: asset={asset_id}, error={str(e)}",
            user=current_user['username'],
            request_id=request_id
        )
        raise CNOPInternalServerException(ErrorMessages.SERVICE_UNAVAILABLE)
