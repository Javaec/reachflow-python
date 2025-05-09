from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional


class Settings(BaseSettings):
    # Telegram API
    TELEGRAM_API_ID: int = Field(..., validation_alias="TELEGRAM_API_ID")
    TELEGRAM_API_HASH: str = Field(..., validation_alias="TELEGRAM_API_HASH")
    SESSION_STRING: Optional[str] = Field(None, validation_alias="SESSION_STRING")

    # Server config (не включаем PORT в модель, чтобы избежать конфликта)
    SERVER_HOST: str = Field("0.0.0.0", validation_alias="HOST")
    RELOAD: bool = Field(False, validation_alias="RELOAD")

    # Security
    SECRET_KEY: str = Field(..., validation_alias="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(1440, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Игнорировать лишние переменные

    @field_validator('TELEGRAM_API_ID')
    def validate_api_id(cls, v):
        if not isinstance(v, int) or v <= 0:
            raise ValueError("API_ID must be positive integer")
        return v


settings = Settings()
