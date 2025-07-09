import jwt
import os
from datetime import datetime, timedelta
from typing import Optional

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-development-secret-key')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

def create_access_token(user_email: str, user_name: str) -> dict:
    """Create JWT access token"""
    now = datetime.utcnow()
    expire = now + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    payload = {
        "sub": user_email,  # Subject (user identifier)
        "name": user_name,
        "iat": now,         # Issued at
        "exp": expire       # Expiration
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_HOURS * 3600,  # seconds
        "expires_at": expire.isoformat()
    }

def verify_access_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
