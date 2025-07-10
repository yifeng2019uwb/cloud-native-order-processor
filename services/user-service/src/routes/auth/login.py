"""
User Login API Endpoint
Path: cloud-native-order-processor/services/user-service/src/routes/auth/login.py
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Union
import sys
import os
import logging
from datetime import datetime, timezone

# Simple path setup - Add common package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "common", "src"))

# Import user-service API models
from models.login_models import (
    UserLoginRequest,
    LoginSuccessResponse,
    LoginErrorResponse
)
from models.shared_models import ErrorResponse
from models.user_models import UserBaseInfo

# Import common DAO models
from models.user import User

# Import dependencies
from .dependencies import get_user_dao
from .token_utils import create_access_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])


@router.post(
    "/login",
    response_model=Union[LoginSuccessResponse, LoginErrorResponse],
    responses={
        200: {
            "description": "Login successful",
            "model": LoginSuccessResponse
        },
        401: {
            "description": "Authentication failed",
            "model": LoginErrorResponse
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse
        }
    }
)
async def login_user(
    login_data: UserLoginRequest,
    user_dao=Depends(get_user_dao)
) -> LoginSuccessResponse:
    """Authenticate user with username and password"""
    try:
        logger.info(f"Login attempt for: {login_data.username}")

        # Authenticate user using username
        user = await user_dao.authenticate_user(login_data.username, login_data.password)
        if not user:
            logger.warning(f"Authentication failed for: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        logger.info(f"User authenticated successfully: {login_data.username}")

        # Create JWT token using username (primary key)
        token_data = create_access_token(user.username, user.name)

        # Use proper response model with all required fields
        return LoginSuccessResponse(
            message="Login successful",
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user=UserBaseInfo(
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                date_of_birth=user.date_of_birth,
                marketing_emails_consent=user.marketing_emails_consent,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for {login_data.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/login/health", status_code=status.HTTP_200_OK)
async def login_health():
    """Health check for login service"""
    return {
        "service": "user-login",
        "status": "healthy",
        "endpoints": [
            "POST /auth/login",
            "GET /auth/login/health"
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }