import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def get_async_engine():
    async_database_url = URL.create(
        drivername="sqlite+aiosqlite",
        database="projectgrading.db",
    )
    async_engine = create_async_engine(async_database_url)
    return async_engine


async_engine = get_async_engine()
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


@asynccontextmanager
async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    from .models import Base  # Import models to register them with Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
