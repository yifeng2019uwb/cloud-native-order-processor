"""
Unit tests for insights API models
"""
import pytest
from datetime import datetime, timezone
from src.api_models.insights.insights_models import InsightsData, GetInsightsResponse
from src.constants import LLM_MODEL_NAME

# Test constants
TEST_SUMMARY = "Your portfolio is well-diversified."
TEST_GENERATED_AT = datetime(2026, 1, 31, 10, 30, 0, tzinfo=timezone.utc)


class TestInsightsData:
    """Test InsightsData model"""

    def test_insights_data_creation(self):
        """Test creating InsightsData"""
        data = InsightsData(
            summary=TEST_SUMMARY,
            generated_at=TEST_GENERATED_AT,
            model=LLM_MODEL_NAME
        )

        assert data.summary == TEST_SUMMARY
        assert data.generated_at == TEST_GENERATED_AT
        assert data.model == LLM_MODEL_NAME

    def test_insights_data_validation(self):
        """Test InsightsData validation"""
        # Should raise error if required fields missing
        with pytest.raises(Exception):
            InsightsData(
                summary=TEST_SUMMARY,
                generated_at=TEST_GENERATED_AT
                # Missing model
            )


class TestGetInsightsResponse:
    """Test GetInsightsResponse model"""

    def test_get_insights_response_creation(self):
        """Test creating GetInsightsResponse"""
        insights_data = InsightsData(
            summary=TEST_SUMMARY,
            generated_at=TEST_GENERATED_AT,
            model=LLM_MODEL_NAME
        )

        response = GetInsightsResponse(data=insights_data)

        assert response.data == insights_data
        assert response.data.summary == TEST_SUMMARY
        assert response.data.model == LLM_MODEL_NAME
