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

# Asset models (consolidated into single file)
from .asset import (
    # Request models
    GetAssetBalanceRequest, GetAssetBalancesRequest, GetPortfolioRequest,
    # Data models
    AssetBalanceData, AssetTransactionData, PortfolioAssetData,
    # Response models
    GetAssetBalanceResponse, GetAssetBalancesResponse, GetAssetTransactionsResponse, GetPortfolioResponse
)

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
    # Asset models (consolidated)
    "GetAssetBalanceRequest",
    "GetAssetBalancesRequest",

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
