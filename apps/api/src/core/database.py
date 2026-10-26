"""
Database Engine & Session Management
Asynchronous SQLAlchemy 2.0 configuration with support for both SQLite and PostgreSQL.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from apps.api.src.core.config import settings

# Configure async engine
# connect_args={"check_same_thread": False} is required only for SQLite
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy database models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an isolated async database session per request.
    Ensures sessions are cleanly closed even if an exception occurs.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
