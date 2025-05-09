import os
import uvicorn
import logging
from pathlib import Path
from fastapi import FastAPI
from core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_uvicorn_config(app: FastAPI) -> dict:
    """Динамическая конфигурация Uvicorn"""
    is_prod = os.getenv("ENV_MODE") == "production"

    config = {
        "app": app,
        "host": settings.SERVER_HOST,
        "log_config": None,
        "port": int(os.getenv("PORT", 8000)),  # PORT берется напрямую из окружения
        "workers": int(os.getenv("WEB_CONCURRENCY", 1)) if is_prod else 1,
        "log_level": "info" if is_prod else "debug"
    }

    if not is_prod:
        config.update({
            "reload": settings.RELOAD,
            "reload_dirs": [str(Path(__file__).parent)],
            "reload_includes": ["*.py"],
            "server_header": False
        })

    return config


if __name__ == "__main__":
    try:
        from main import app  # Импорт после настройки окружения

        logger.info("Starting server...")
        config = get_uvicorn_config(app)
        logger.info(f"Server config: {config}")

        uvicorn.run(**config)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
