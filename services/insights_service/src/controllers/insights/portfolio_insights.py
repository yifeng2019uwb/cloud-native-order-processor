"""
Portfolio Insights Controller
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from common.auth.security.auth_dependencies import AuthenticatedUser, get_current_user
from common.shared.constants.api_constants import HTTPStatus
from common.shared.logging import BaseLogger, LoggerName, LogAction

from api_models.insights.insights_models import GetInsightsResponse, InsightsData
from api_info_enum import ApiPaths, ApiTags
from constants import (
    MSG_ERROR_INSIGHTS_NOT_CONFIGURED,
    MSG_ERROR_INSIGHTS_TIMEOUT,
    MSG_ERROR_INSIGHTS_FAILED,
    MSG_ERROR_INSIGHTS_RATE_LIMITED,
    MSG_SUCCESS_INSIGHTS_GENERATED,
    MSG_ERROR_EMPTY_PORTFOLIO,
    MSG_ERROR_INVALID_USER_CONTEXT,
    MSG_ERROR_UNEXPECTED,
    LLM_MODEL_NAME,
    ERROR_KEYWORD_TIMEOUT,
    ERROR_KEYWORD_TIMED_OUT,
    ERROR_KEYWORD_RATE_LIMIT,
    ERROR_CODE_RATE_LIMIT,
    MSG_ERROR_LLM_BLOCKED
)
from controllers.dependencies import get_data_aggregator, get_llm_service
from services.data_aggregator import DataAggregator
from services.llm_service import LLMService
from services.insights_cache import (
    compute_portfolio_hash,
    get_cached,
    save_cached,
)

logger = BaseLogger(LoggerName.INSIGHTS)
router = APIRouter(tags=[ApiTags.INSIGHTS.value])


@router.get(ApiPaths.PORTFOLIO_INSIGHTS.value, response_model=GetInsightsResponse)
def get_portfolio_insights(
    current_user: AuthenticatedUser = Depends(get_current_user),
    data_aggregator: DataAggregator = Depends(get_data_aggregator),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Get AI-generated portfolio insights

    Requires authentication via JWT token.
    """
    username = current_user.username
    if not username:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=MSG_ERROR_INVALID_USER_CONTEXT
        )

    # Check if LLM service is configured
    if llm_service is None:
        logger.warning(action=LogAction.ERROR, message=MSG_ERROR_INSIGHTS_NOT_CONFIGURED, user=username)
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail=MSG_ERROR_INSIGHTS_NOT_CONFIGURED
        )

    try:
        # Aggregate portfolio data
        portfolio_context = data_aggregator.aggregate_portfolio_data(username)

        # Handle empty portfolio
        if portfolio_context.total_portfolio_value == 0 and len(portfolio_context.holdings) == 0:
            return GetInsightsResponse(
                data=InsightsData(
                    summary=MSG_ERROR_EMPTY_PORTFOLIO,
                    generated_at=datetime.now(timezone.utc),
                    model=LLM_MODEL_NAME
                )
            )

        # Check in-memory cache (24h TTL)
        portfolio_hash = compute_portfolio_hash(portfolio_context)
        cached = get_cached(username, portfolio_hash)
        if cached:
            summary, generated_at, model = cached
            return GetInsightsResponse(
                data=InsightsData(summary=summary, generated_at=generated_at, model=model)
            )

        # Generate insights via LLM
        try:
            summary = llm_service.generate_insights(portfolio_context)
        except ValueError as e:
            error_msg = str(e)
            # Handle blocked responses gracefully (return 429 for rate limits/blocking)
            if MSG_ERROR_LLM_BLOCKED in error_msg:
                logger.warning(action=LogAction.ERROR, message=f"LLM blocked response: {error_msg}", user=username)
                raise HTTPException(
                    status_code=HTTPStatus.TOO_MANY_REQUESTS,
                    detail=MSG_ERROR_LLM_BLOCKED
                )
            else:
                logger.error(action=LogAction.ERROR, message=f"{MSG_ERROR_INSIGHTS_FAILED}: {error_msg}", user=username)
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=MSG_ERROR_INSIGHTS_FAILED
                )
        except Exception as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                logger.error(action=LogAction.ERROR, message=MSG_ERROR_INSIGHTS_TIMEOUT, user=username)
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=MSG_ERROR_INSIGHTS_TIMEOUT
                )
            elif ERROR_KEYWORD_RATE_LIMIT in error_msg or ERROR_CODE_RATE_LIMIT in error_msg:
                logger.error(action=LogAction.ERROR, message=MSG_ERROR_INSIGHTS_RATE_LIMITED, user=username)
                raise HTTPException(
                    status_code=HTTPStatus.TOO_MANY_REQUESTS,
                    detail=MSG_ERROR_INSIGHTS_RATE_LIMITED
                )
            else:
                logger.error(action=LogAction.ERROR, message=f"{MSG_ERROR_INSIGHTS_FAILED}: {str(e)}", user=username)
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=MSG_ERROR_INSIGHTS_FAILED
                )

        logger.info(action=LogAction.REQUEST_END, message=MSG_SUCCESS_INSIGHTS_GENERATED, user=username)

        # Save to cache for next request
        save_cached(username, portfolio_hash, summary, LLM_MODEL_NAME)

        return GetInsightsResponse(
            data=InsightsData(
                summary=summary,
                generated_at=datetime.now(timezone.utc),
                model=LLM_MODEL_NAME
            )
        )

    except HTTPException:
        raise
    except ValueError as e:
        # User not found
        logger.warning(action=LogAction.VALIDATION_ERROR, message=str(e), user=username)
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(action=LogAction.ERROR, message=f"{MSG_ERROR_UNEXPECTED}: {str(e)}\n{error_traceback}", user=username)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"{MSG_ERROR_UNEXPECTED}: {str(e)}"
        )
