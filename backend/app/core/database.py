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
POSTGRES_URI = settings.POSTGRES_URI
SQLALCHEMY_DATABASE_URL = POSTGRES_URI.replace("postgres://", "postgresql+asyncpg://")
SSL_MODE = settings.POSTGRES_SSL_MODE

# SSL Context setup
current_dir = os.path.dirname(os.path.abspath(__file__))
ca_file_path = os.path.join(current_dir, "ca.pem")
ssl_context = ssl.create_default_context(cafile=ca_file_path)

if SSL_MODE == "require":
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
elif SSL_MODE == "verify-full":
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    # You might want to specify CA certificate if needed
    # ssl_context.load_verify_locations("/path/to/ca.pem")
elif SSL_MODE == "verify-ca":
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_REQUIRED
elif SSL_MODE == "disable":
    ssl_context = None
else:
    raise ValueError(f"Invalid SSL mode: {SSL_MODE}")

# Connection arguments
connect_args = {"server_settings": {"application_name": "agent-writer"}}

# Add SSL context if SSL is enabled
if ssl_context:
    connect_args["ssl"] = ssl_context

# Create async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
    connect_args=connect_args,
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
