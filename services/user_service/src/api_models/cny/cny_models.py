"""CNY claim API models."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CnyClaimRequest(BaseModel):
    """Request model for CNY claim."""
    phrase: str = Field(..., min_length=1, description="Secret phrase to claim")


class CnyClaimResponse(BaseModel):
    """Response model for CNY claim."""
    success: bool
    message: str
    amount: Decimal
    got_red_pocket: bool
    timestamp: datetime
