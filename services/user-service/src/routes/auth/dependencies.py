"""
Basic FastAPI dependencies for authentication (Registration-focused)
Path: /Users/yifengzhang/workspace/cloud-native-order-processor/services/user-service/src/routes/auth/dependencies.py
"""
import sys
import os

# Add common package to path
common_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "common", "src")
sys.path.insert(0, common_path)

from fastapi import Depends, HTTPException, status
import logging

from database.dao.user_dao import UserDAO
from database.dynamodb_connection import get_dynamodb

logger = logging.getLogger(__name__)


async def get_user_dao():
    """
    Get UserDAO instance dependency - properly handles async generator
    """
    try:
        # get_dynamodb() is an async generator, so we need to iterate it
        async for db_connection in get_dynamodb():
            dao = UserDAO(db_connection)
            logger.debug("UserDAO instance created")
            yield dao
            break  # We only need one connection
    except Exception as e:
        logger.error(f"Failed to create UserDAO: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service unavailable"
        )


# Placeholder for future token-related dependencies
async def verify_token_dependency():
    """
    Placeholder for token verification dependency
    Will be implemented in login/profile endpoints
    """
    pass


async def get_current_user():
    """
    Placeholder for current user dependency
    Will be implemented in profile endpoints
    """
    pass
