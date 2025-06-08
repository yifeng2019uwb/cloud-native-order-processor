import os
import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        # Build the database URL from Terraform-created infrastructure
        self.database_url = self._build_database_url()
        self.pool = None

    def _build_database_url(self) -> str:
        """Build database URL from environment variables set by Terraform deployment"""

        # Primary approach: Use complete DATABASE_URL if provided
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url

        # Secondary approach: Build from individual components
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "orderprocessor")
        db_user = os.getenv("DB_USER", "orderuser")
        db_password = os.getenv("DB_PASSWORD")

        if db_host and db_password:
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        # Fallback for local development only
        logger.warning(
            "Using localhost database URL - this should only happen in local development"
        )
        fallback_password = os.getenv("DB_PASSWORD", "ChangeThisPassword123!")
        return (
            f"postgresql://orderuser:{fallback_password}@localhost:5432/orderprocessor"
        )

    async def init_pool(self):
        """Initialize connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.database_url, min_size=1, max_size=10, command_timeout=60
            )
            logger.info("Database connection pool initialized")

    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database connection pool closed")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get database connection from pool"""
        if not self.pool:
            await self.init_pool()

        async with self.pool.acquire() as connection:
            yield connection


# Global database manager instance
db_manager = DatabaseManager()


# Dependency for FastAPI
async def get_db():
    async with db_manager.get_connection() as conn:
        yield conn
