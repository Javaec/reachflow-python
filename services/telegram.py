from pyrogram import Client
from pyrogram.errors import AuthKeyUnregistered, BadRequest
import logging
from core.config import settings
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramService:
    _client: Optional[Client] = None
    _is_ready = asyncio.Event()

    @classmethod
    async def initialize(cls):
        if cls._client and await cls._is_connected():
            return

        try:
            cls._client = Client(
                "tg_web_session",
                api_id=settings.TELEGRAM_API_ID,
                api_hash=settings.TELEGRAM_API_HASH,
                session_string=settings.SESSION_STRING or None,
                in_memory=True
            )

            if settings.SESSION_STRING:
                await cls._client.start()
                cls._is_ready.set()
                logger.info("Telegram client initialized with existing session")

        except (AuthKeyUnregistered, BadRequest) as e:
            logger.error(f"Session invalid: {e}")
            await cls.shutdown()
            raise RuntimeError("Invalid session, please re-authenticate")

    @classmethod
    async def shutdown(cls):
        try:
            if cls._client and await cls._is_connected():
                await cls._client.stop()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            cls._client = None
            cls._is_ready.clear()

    @classmethod
    async def _is_connected(cls) -> bool:
        return cls._client and await cls._client.is_connected()

    @classmethod
    async def is_ready(cls) -> bool:
        return cls._is_ready.is_set() and await cls._is_connected()

    @classmethod
    async def get_client(cls) -> Client:
        if not await cls.is_ready():
            raise RuntimeError("Telegram client not ready")
        return cls._client
