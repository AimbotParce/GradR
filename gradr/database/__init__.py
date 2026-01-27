import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def get_async_engine(db_path: str | Path = "grading.db"):
    async_database_url = URL.create(drivername="sqlite+aiosqlite", database=str(db_path))
    async_engine = create_async_engine(async_database_url)
    return async_engine


async_engine: AsyncEngine
AsyncSessionLocal: async_sessionmaker


@asynccontextmanager
async def get_async_session() -> AsyncIterator[AsyncSession]:
    assert "AsyncSessionLocal" in globals(), "Database not registered. Call register_database first."
    async with AsyncSessionLocal() as session:
        yield session


async def register_database(db_path: str | Path = "grading.db"):
    global async_engine, AsyncSessionLocal
    async_engine = get_async_engine(db_path)
    AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def create_tables():
    assert "async_engine" in globals(), "Database not registered. Call register_database first."
    from .models import Base  # Import models to register them with Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
