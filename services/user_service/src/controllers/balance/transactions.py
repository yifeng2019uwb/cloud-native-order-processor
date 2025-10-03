"""
Transactions API Endpoint
Path: services/user_service/src/controllers/balance/transactions.py

Layer 2: Business validation (in service layer)
Layer 1: Field validation (handled in API models)
"""
from datetime import datetime, timezone
from typing import Union
from fastapi import APIRouter, HTTPException, Depends, status, Request
from api_models.balance import TransactionListResponse, TransactionResponse
from api_models.shared.common import ErrorResponse
from common.data.database.dependencies import get_balance_dao
from common.data.entities.user import User
from common.exceptions.shared_exceptions import CNOPInternalServerException
from common.shared.logging import BaseLogger, Loggers, LogActions
from common.shared.constants.error_messages import ErrorMessages
from common.shared.constants.api_responses import APIResponseDescriptions
from common.shared.constants.http_status import HTTPStatus
from api_info_enum import ApiTags, ApiPaths, ApiResponseKeys
from controllers.auth.dependencies import get_current_user
from controllers.dependencies import get_request_id_from_request

# Local constants for this controller only
MSG_SUCCESS_TRANSACTIONS_RETRIEVED = "Transactions retrieved successfully"

# Initialize our standardized logger
logger = BaseLogger(Loggers.USER)
router = APIRouter(tags=[ApiTags.BALANCE.value])


@router.get(
    ApiPaths.TRANSACTIONS.value,
    response_model=Union[TransactionListResponse, ErrorResponse],
    responses={
        HTTPStatus.OK: {
            ApiResponseKeys.DESCRIPTION.value: MSG_SUCCESS_TRANSACTIONS_RETRIEVED,
            ApiResponseKeys.MODEL.value: TransactionListResponse
        },
        HTTPStatus.UNAUTHORIZED: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_UNAUTHORIZED,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.NOT_FOUND: {
            ApiResponseKeys.DESCRIPTION.value: ErrorMessages.USER_NOT_FOUND,
            ApiResponseKeys.MODEL.value: ErrorResponse
        },
        HTTPStatus.SERVICE_UNAVAILABLE: {
            ApiResponseKeys.DESCRIPTION.value: APIResponseDescriptions.ERROR_SERVICE_UNAVAILABLE,
            ApiResponseKeys.MODEL.value: ErrorResponse
        }
    }
)
def get_user_transactions(
    request: Request,
    current_user: User = Depends(get_current_user),
    balance_dao = Depends(get_balance_dao)
) -> TransactionListResponse:
    """
    Get user transaction history

    Layer 1: Field validation already handled in API models
    Layer 2: Business validation (user authentication, etc.)
    """
    # Extract request_id from headers using existing method
    request_id = get_request_id_from_request(request)

    try:
        logger.info(action=LogActions.REQUEST_START, message=f"Transaction history request for user: {current_user.username}", request_id=request_id)

        # Get transactions from database
        transactions, _ = balance_dao.get_user_transactions(current_user.username)

        if transactions is None:
            transactions = []  # Empty list if no transactions

        transaction_responses = []
        for transaction in transactions:
            transaction_responses.append(TransactionResponse(
                transaction_id=str(transaction.transaction_id),
                transaction_type=transaction.transaction_type.value,
                amount=transaction.amount,
                status=transaction.status.value,
                created_at=transaction.created_at
            ))

        logger.info(action=LogActions.REQUEST_END, message=f"Transaction history retrieved successfully for user: {current_user.username}", request_id=request_id)

        return TransactionListResponse(
            transactions=transaction_responses,
            total_count=len(transaction_responses)
        )

    except Exception as e:
        logger.error(action=LogActions.ERROR, message=f"Failed to get transactions for user {current_user.username}: {str(e)}", request_id=request_id)
        raise CNOPInternalServerException(f"Failed to get transactions: {str(e)}")