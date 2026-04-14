"""Application configuration via Pydantic BaseSettings."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "Zircon FRT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = Field(default="change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = Field(default="postgresql+asyncpg://zircon:zircon@postgres:5432/zircon")
    DATABASE_URL_SYNC: str = Field(default="postgresql://zircon:zircon@postgres:5432/zircon")

    # Redis
    REDIS_URL: str = Field(default="redis://redis:6379/0")

    # Elasticsearch
    ELASTICSEARCH_URL: str = Field(default="http://elasticsearch:9200")
    ELASTICSEARCH_INDEX: str = "zircon_files"

    # ClamAV
    CLAMAV_HOST: str = Field(default="clamav")
    CLAMAV_PORT: int = Field(default=3310)

    # File storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB

    # Encryption key for API keys (32 bytes base64-encoded)
    ENCRYPTION_KEY: str = Field(default="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
