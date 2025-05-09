from fastapi import FastAPI
import uvicorn
import logging
from services.telegram import TelegramService
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Proxy API")


async def initialize_telegram():
    """Отдельная задача для инициализации Telegram"""
    try:
        await TelegramService.init()
    except Exception as e:
        logger.error(f"Telegram initialization failed: {e}")
        raise


@app.on_event("startup")
async def startup():
    # Запускаем инициализацию в фоне без ожидания
    asyncio.create_task(initialize_telegram())


@app.get("/health")
async def health_check():
    try:
        await TelegramService.wait_ready()
        return {"status": "ok", "telegram": "connected"}
    except Exception:
        return {"status": "ok", "telegram": "connecting"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
