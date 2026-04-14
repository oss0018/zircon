"""Async SQLAlchemy database setup."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

_engine: Optional[AsyncEngine] = None
_session_factory = None


def get_engine() -> AsyncEngine:
    """Get or create the async engine (lazy initialization)."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    return _engine


def get_session_factory():
    """Get or create the session factory (lazy initialization)."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)
    return _session_factory


AsyncSessionLocal = get_session_factory


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency for getting async DB session."""
    async with get_session_factory()() as session:
        try:
            yield session
        finally:
            await session.close()
