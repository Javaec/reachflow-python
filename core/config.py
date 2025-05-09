from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key"
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    SESSION_STRING: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 часа

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
