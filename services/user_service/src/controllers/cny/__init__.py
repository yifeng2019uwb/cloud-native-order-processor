"""CNY router."""
from fastapi import APIRouter

from .claim import router as claim_router

router = APIRouter(prefix="/cny")
router.include_router(claim_router)
