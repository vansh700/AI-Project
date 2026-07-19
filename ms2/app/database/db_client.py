"""Async SQLAlchemy engine and session factory for MS2 PostgreSQL database.

This module owns the connection lifecycle for the MS2 planner state database.
All database operations must go through get_session().
"""
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config.logger import get_logger

load_dotenv()
logger = get_logger("ms2.database.db_client")

_engine = None
_session_factory = None


def _get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv("MS2_DB_URL")
        if not db_url:
            raise RuntimeError("MS2_DB_URL environment variable is not set")
        _engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
        logger.info("MS2 database engine initialised | url=%s", db_url.split("@")[-1])
    return _engine


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(_get_engine(), expire_on_commit=False)
    return _session_factory


@asynccontextmanager
async def get_session():
    """Async context manager yielding a single database session."""
    async with _get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables() -> None:
    """Create all MS2 tables if they do not exist. Called on startup."""
    from app.database.models import Base  # local import to avoid circular deps
    async with _get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("MS2 database tables verified/created")


async def close_engine() -> None:
    """Dispose the database engine on shutdown."""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
        logger.info("MS2 database engine closed")
