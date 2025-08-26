#!/usr/bin/env python3
"""
Redis usage examples for the order processor services
Demonstrates caching, session management, and token blacklisting
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from ..data.database.redis_connection import (
    get_redis_client,
    redis_set,
    redis_get,
    redis_delete,
    redis_exists,
    get_redis_namespace
)
from ..data.database.redis_config import is_production

logger = logging.getLogger(__name__)

class RedisCache:
    """Simple Redis cache implementation"""

    def __init__(self, namespace: Optional[str] = None):
        self.namespace = namespace or get_redis_namespace()
        self.client = get_redis_client()

    def _get_key(self, key: str) -> str:
        """Get namespaced key"""
        return f"{self.namespace}:{key}"

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set cache value with optional expiration"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, str):
                value = str(value)

            return redis_set(self._get_key(key), value, expire)
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            value = redis_get(self._get_key(key))
            if value is None:
                return None

            # Try to parse as JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete cache key"""
        return redis_delete(self._get_key(key))

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return redis_exists(self._get_key(key))

class TokenBlacklist:
    """JWT token blacklist using Redis"""

    def __init__(self):
        self.cache = RedisCache("tokens")

    def blacklist_token(self, token: str, expires_at: datetime) -> bool:
        """Add token to blacklist"""
        try:
            # Calculate TTL in seconds
            ttl = int((expires_at - datetime.now()).total_seconds())
            if ttl <= 0:
                return False  # Token already expired

            # Store token with expiration
            return self.cache.set(f"blacklist:{token}", "1", ttl)
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False

    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        return self.cache.exists(f"blacklist:{token}")

    def remove_from_blacklist(self, token: str) -> bool:
        """Remove token from blacklist"""
        return self.cache.delete(f"blacklist:{token}")

class SessionManager:
    """User session management using Redis"""

    def __init__(self):
        self.cache = RedisCache("sessions")
        self.session_ttl = 3600  # 1 hour default

    def create_session(self, username: str, session_data: Dict[str, Any]) -> str:
        """Create user session"""
        try:
            session_id = f"session:{username}:{datetime.now().timestamp()}"
            session_data["created_at"] = datetime.now().isoformat()
            session_data["username"] = username

            if self.cache.set(session_id, session_data, self.session_ttl):
                return session_id
            return None
        except Exception as e:
            logger.error(f"Failed to create session for user {username}: {e}")
            return None

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.cache.get(session_id)

    def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            current_data = self.get_session(session_id)
            if current_data:
                current_data.update(session_data)
                current_data["updated_at"] = datetime.now().isoformat()
                return self.cache.set(session_id, current_data, self.session_ttl)
            return False
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        return self.cache.delete(session_id)

    def extend_session(self, session_id: str) -> bool:
        """Extend session TTL"""
        try:
            session_data = self.get_session(session_id)
            if session_data:
                return self.cache.set(session_id, session_data, self.session_ttl)
            return False
        except Exception as e:
            logger.error(f"Failed to extend session {session_id}: {e}")
            return False

# Usage examples
def example_cache_usage():
    """Example of using Redis cache"""
    cache = RedisCache("example")

    # Cache user data
    user_data = {
        "id": "user123",
        "name": "John Doe",
        "email": "john@example.com",
        "last_login": datetime.now().isoformat()
    }

    # Set cache with 1 hour expiration
    cache.set("user:user123", user_data, 3600)

    # Get cached data
    cached_user = cache.get("user:user123")
    print(f"Cached user: {cached_user}")

    # Check if exists
    exists = cache.exists("user:user123")
    print(f"User exists in cache: {exists}")

def example_token_blacklist():
    """Example of token blacklisting"""
    blacklist = TokenBlacklist()

    # Simulate token expiration
    expires_at = datetime.now() + timedelta(hours=1)

    # Blacklist a token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    blacklist.blacklist_token(token, expires_at)

    # Check if blacklisted
    is_blacklisted = blacklist.is_blacklisted(token)
    print(f"Token is blacklisted: {is_blacklisted}")

def example_session_management():
    """Example of session management"""
    session_mgr = SessionManager()

    # Create session
    user_data = {
        "name": "John Doe",
        "role": "user",
        "preferences": {"theme": "dark", "language": "en"}
    }

    session_id = session_mgr.create_session("user123", user_data)
    print(f"Created session: {session_id}")

    # Get session
    session = session_mgr.get_session(session_id)
    print(f"Session data: {session}")

    # Update session
    session_mgr.update_session(session_id, {"last_activity": datetime.now().isoformat()})

    # Extend session
    session_mgr.extend_session(session_id)

if __name__ == "__main__":
    # Run examples
    print("=== Redis Cache Example ===")
    example_cache_usage()

    print("\n=== Token Blacklist Example ===")
    example_token_blacklist()

    print("\n=== Session Management Example ===")
    example_session_management()