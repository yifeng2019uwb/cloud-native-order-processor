"""
API Models Package for Order Service
Path: services/order_service/src/api_models/__init__.py
"""

# Order models (consolidated)
from .order import (
    # Request models
    OrderCreateRequest, GetOrderRequest, OrderListRequest, OrderFilterRequest,
    OrderCancelRequest, OrderHistoryRequest,
    # Response models
    OrderData, OrderCreateResponse, GetOrderResponse, OrderListResponse,
    OrderSummary, OrderCancelResponse, OrderHistoryItem, OrderHistoryResponse
)

# Asset models (for portfolio functionality)
from .asset_requests import GetAssetBalanceRequest, GetAssetBalancesRequest, GetAssetTransactionsRequest, GetPortfolioRequest
from .asset_responses import AssetBalanceData, AssetTransactionData, PortfolioAssetData, GetAssetBalanceResponse, GetAssetBalancesResponse, GetAssetTransactionsResponse, GetPortfolioResponse

# Shared models
from .shared.common import BaseResponse, SuccessResponse, ErrorResponse, ValidationErrorResponse

__all__ = [
    # Order models
    "OrderCreateRequest",
    "GetOrderRequest",
    "OrderListRequest",
    "OrderFilterRequest",
    "OrderCancelRequest",
    "OrderHistoryRequest",
    "OrderData",
    "OrderCreateResponse",
    "GetOrderResponse",
    "OrderListResponse",
    "OrderSummary",
    "OrderCancelResponse",
    "OrderHistoryItem",
    "OrderHistoryResponse",
    # Asset models (for portfolio functionality)
    "GetAssetBalanceRequest",
    "GetAssetBalancesRequest",
    "GetAssetTransactionsRequest",
    "GetPortfolioRequest",
    "AssetBalanceData",
    "AssetTransactionData",
    "PortfolioAssetData",
    "GetAssetBalanceResponse",
    "GetAssetBalancesResponse",
    "GetAssetTransactionsResponse",
    "GetPortfolioResponse",
    # Shared models
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "ValidationErrorResponse"
]
