import os
import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://orderuser:ChangeThisPassword123!@localhost:5432/orderprocessor",
        )
        self.pool = None

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
