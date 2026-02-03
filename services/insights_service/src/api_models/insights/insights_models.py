"""
Insights API Models
"""
from datetime import datetime
from pydantic import BaseModel, Field


class InsightsData(BaseModel):
    """The insights content returned to frontend"""
    summary: str = Field(..., description="2-4 sentence analysis from LLM")
    generated_at: datetime = Field(..., description="When analysis was generated")
    model: str = Field(..., description="LLM model used (e.g., 'gemini-1.5-flash')")


class GetInsightsResponse(BaseModel):
    """API response - follows existing service patterns"""
    data: InsightsData
