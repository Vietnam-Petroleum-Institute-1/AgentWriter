from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AgentWriter API"
    PROJECT_VERSION: str = "1.0.0"

    CORS_ORIGINS: List[str] = ["*"]

    # Database configs
    POSTGRES_URL: str
    POSTGRES_SSL_MODE: str = "require"

    # JWT configs
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # Dify configs
    DIFY_API_KEY: str
    DIFY_API_URL: str

    # App configs
    SECRET_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True
        # Cho phép extra fields trong .env
        extra = "ignore"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()