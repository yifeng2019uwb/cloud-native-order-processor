"""
Health Controller

Health check endpoints for Kubernetes probes.
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    pass
