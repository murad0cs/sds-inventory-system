from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import AsyncSessionLocal
import asyncpg
from app.core.config import settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_asyncpg_connection():
    conn = await asyncpg.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        database=settings.DATABASE_NAME
    )
    try:
        yield conn
    finally:
        await conn.close()