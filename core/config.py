from pydantic import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "secret-key-for-sessions"
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    SESSION_STRING: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()