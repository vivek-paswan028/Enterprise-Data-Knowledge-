from typing import AsyncGenerator, Generator, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from src.config.settings import settings
from src.utils.logger import export_logger as logger


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy 2.0 ORM models."""
    pass


_sync_engine: Optional[Engine] = None
_async_engine: Optional[AsyncEngine] = None


def get_sync_engine() -> Engine:
    global _sync_engine
    if _sync_engine is None:
        try:
            _sync_engine = create_engine(
                settings.SYNC_DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
        except Exception:
            logger.warning("PostgreSQL driver unavailable. Falling back to SQLite for local session execution.")
            _sync_engine = create_engine("sqlite:///./datapulse_warehouse.db", echo=False)
    return _sync_engine


def get_sync_db() -> Generator[Session, None, None]:
    """Dependency injection session generator for sync operations."""
    engine = get_sync_engine()
    SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_async_engine() -> AsyncEngine:
    global _async_engine
    if _async_engine is None:
        try:
            _async_engine = create_async_engine(
                settings.ASYNC_DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
        except Exception:
            _async_engine = create_async_engine("sqlite+aiosqlite:///./datapulse_warehouse.db", echo=False)
    return _async_engine


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection session generator for async FastAPI routes."""
    engine = get_async_engine()
    AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
