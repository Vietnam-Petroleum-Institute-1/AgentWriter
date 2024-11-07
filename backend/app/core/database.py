import os
import ssl
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

load_dotenv()


# Convert standard postgres:// URL to postgresql+asyncpg:// for async driver
SQLALCHEMY_DATABASE_URL = settings.POSTGRES_URL


# Create async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
