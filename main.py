from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator
from core.config import settings
from services.telegram import TelegramService
from routers import auth, messaging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Управление жизненным циклом приложения"""
    logger.info("Application starting...")

    try:
        # Инициализация сервисов
        await TelegramService.initialize()
        logger.info("Services initialized")

        yield

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    finally:
        logger.info("Application shutting down...")
        await TelegramService.shutdown()
        logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Фабрика приложений"""
    app = FastAPI(
        title="Telegram Web Client",
        description="Full-featured Telegram web interface",
        version=settings.APP_VERSION if hasattr(settings, 'APP_VERSION') else "1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if not os.getenv("PRODUCTION") else None,
        redoc_url=None
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Роутеры
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(messaging.router, prefix="/api", tags=["Messaging"])

    # Health check
    @app.get("/health", status_code=status.HTTP_200_OK, tags=["Utility"])
    async def health_check():
        return {
            "status": "healthy",
            "services": {
                "telegram": await TelegramService.is_ready()
            }
        }

    return app


app = create_app()
