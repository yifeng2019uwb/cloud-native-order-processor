"""CNY claim API endpoint."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status

from api_models.cny import CnyClaimRequest, CnyClaimResponse
from common.data.entities.user import User
from controllers.auth.dependencies import get_current_user
from controllers.dependencies import get_balance_dao_dependency
from services.cny_claim import CNYClaimService

from user_exceptions import CNOPAlreadyClaimedTodayException

router = APIRouter(tags=["cny"])


def get_cny_claim_service() -> CNYClaimService:
    """Get CNYClaimService instance."""
    return CNYClaimService()


@router.post(
    "/claim",
    response_model=CnyClaimResponse,
    status_code=status.HTTP_201_CREATED,
)
async def claim(
    body: CnyClaimRequest,
    current_user: User = Depends(get_current_user),
    balance_dao=Depends(get_balance_dao_dependency),
    cny_service: CNYClaimService = Depends(get_cny_claim_service),
) -> CnyClaimResponse:
    """Claim CNY red pocket with secret phrase."""
    _, amount, got_red_pocket = await cny_service.claim_reward(
        balance_dao, current_user.username, body.phrase
    )
    msg = "Red pocket!" if got_red_pocket else "Here's a little surprise!"
    return CnyClaimResponse(
        success=True,
        message=msg,
        amount=amount,
        got_red_pocket=got_red_pocket,
        timestamp=datetime.now(timezone.utc),
    )
