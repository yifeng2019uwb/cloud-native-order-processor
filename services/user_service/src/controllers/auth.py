from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta
import logging
import os

from common.entities.user import UserCreate, UserResponse, UserLogin
from common.entities.auth import TokenResponse
from common.dao.user_dao import UserDAO
from common.database.dynamodb_connection import get_dynamodb
logger = logging.getLogger(__name__)

print("🔍 AUTH.PY FILE IS BEING LOADED")
from fastapi import APIRouter

# Router setup
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.post("/test")
async def test_endpoint():
    return {"message": "Auth routes working!"}

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def create_access_token(email: str) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token and return email"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    email: str = Depends(verify_token),
    db_connection = Depends(get_dynamodb)
) -> UserResponse:
    """Get current authenticated user"""
    user_dao = UserDAO(db_connection)
    user = await user_dao.get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return UserResponse(
        email=user.email,
        username=user.username,
        phone=user.phone,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db_connection = Depends(get_dynamodb)
):
    """Register a new user"""
    try:
        user_dao = UserDAO(db_connection)
        user = await user_dao.create_user(user_data)

        logger.info(f"User registered successfully: {user.email}")

        return UserResponse(
            email=user.email,
            username=user.username,
            phone=user.phone,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    except ValueError as e:
        # User already exists or validation error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    db_connection = Depends(get_dynamodb)
):
    """Authenticate user and return JWT token"""
    try:
        user_dao = UserDAO(db_connection)
        user = await user_dao.authenticate_user(login_data.email, login_data.password)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Create access token
        access_token = create_access_token(user.email)

        logger.info(f"User logged in successfully: {user.email}")

        return TokenResponse(access_token=access_token)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user profile (protected endpoint)"""
    return current_user


@router.post("/logout")
async def logout_user():
    """Logout user (stateless JWT - just return success)"""
    # Note: With stateless JWT, logout is handled client-side
    # In production, you might want to implement token blacklisting
    return {"message": "Logged out successfully"}