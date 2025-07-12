"""
Database configuration and connection management for InsightVault Phase 3.
Uses asyncpg for PostgreSQL connections with async/await support.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
try:
    from sqlalchemy.ext.asyncio import async_sessionmaker  # SQLAlchemy 2.x
except ImportError:
    async_sessionmaker = None  # For SQLAlchemy 1.4.x compatibility
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import os
from typing import AsyncGenerator

# Database URL - supports both PostgreSQL and SQLite for development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./insightvault.db"  # Default to SQLite for development
)

# For development, you can also use SQLite
if os.getenv("USE_SQLITE", "true").lower() == "true":  # Default to true
    DATABASE_URL = "sqlite+aiosqlite:///./insightvault.db"

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    poolclass=NullPool if "sqlite" in DATABASE_URL else None,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create sync engine for sync endpoints (e.g., auth)
# Convert async URL to sync URL
sync_database_url = DATABASE_URL
if "postgresql+asyncpg://" in sync_database_url:
    sync_database_url = sync_database_url.replace("postgresql+asyncpg://", "postgresql://")
elif "sqlite+aiosqlite://" in sync_database_url:
    sync_database_url = sync_database_url.replace("sqlite+aiosqlite://", "sqlite://")

sync_engine = create_engine(
    sync_database_url,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    connect_args={"check_same_thread": False} if "sqlite" in sync_database_url else {},
)

# Synchronous session factory for sync endpoints (e.g., auth)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Create async session factory (only if async_sessionmaker is available)
if async_sessionmaker:
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
else:
    AsyncSessionLocal = None

# Base class for models
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    Yields an async database session.
    """
    if not AsyncSessionLocal:
        raise RuntimeError("async_sessionmaker is not available in this SQLAlchemy version.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db():
    """
    Dependency to get synchronous database session.
    Yields a sync database session for auth endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """
    Close database connections.
    """
    await async_engine.dispose() 