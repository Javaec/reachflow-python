from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "secret-key-for-sessions"
    TELEGRAM_API_ID: int  # Должно быть числом!
    TELEGRAM_API_HASH: str
    SESSION_STRING: str | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 минут время жизни токена

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Инициализация с обработкой ошибок
try:
    settings = Settings()
except Exception as e:
    print(f"Ошибка загрузки конфигурации: {e}")
    raise
