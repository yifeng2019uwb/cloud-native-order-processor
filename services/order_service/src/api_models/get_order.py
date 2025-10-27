"""
Pydantic models specific to get order API
"""
from pydantic import BaseModel, Field, field_validator

# Import centralized field validation functions
from validation.field_validators import validate_order_id

ORDER_ID_FIELD = "order_id"

# Import shared data models
from .shared.data_models import OrderData


class GetOrderRequest(BaseModel):
    """Request model for GET /orders/{order_id}"""

    order_id: str = Field(..., description="Order ID to retrieve")

    @field_validator(ORDER_ID_FIELD)
    @classmethod
    def validate_order_id_format(cls, v: str) -> str:
        """Layer 1: Basic format validation for order_id"""
        return validate_order_id(v)


class GetOrderResponse(BaseModel):
    """Response model for GET /orders/{order_id}"""

    data: OrderData
