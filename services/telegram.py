from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, BadRequest
import logging
from core.config import settings
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramService:
    _client: Optional[Client] = None
    _auth_event = asyncio.Event()

    @classmethod
    async def init(cls):
        """Инициализация с неограниченным временем для авторизации"""
        if cls._client and cls._client.is_connected:
            return

        try:
            cls._client = Client(
                "tg_web_session",
                api_id=settings.TELEGRAM_API_ID,
                api_hash=settings.TELEGRAM_API_HASH,
                session_string=settings.SESSION_STRING or None,
                in_memory=True
            )

            await cls._client.connect()

            if not settings.SESSION_STRING:
                logger.info("Starting new authorization flow...")
                await cls._perform_new_auth()
            else:
                await cls._client.start()

            logger.info("Telegram client initialized successfully")
            cls._auth_event.set()

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            await cls._safe_stop()
            raise

    @classmethod
    async def _perform_new_auth(cls):
        """Авторизация с ручным вводом данных"""
        if not cls._client:
            raise RuntimeError("Client not initialized")

        try:
            phone = input("Enter phone number (e.g. +79123456789): ").strip()
            sent_code = await cls._client.send_code(phone)

            code = input("Enter SMS code: ").strip()
            await cls._client.sign_in(phone, sent_code.phone_code_hash, code)

        except SessionPasswordNeeded:
            password = input("Enter 2FA password: ").strip()
            await cls._client.check_password(password)

        # Сохраняем сессию
        settings.SESSION_STRING = await cls._client.export_session_string()
        logger.info("New session created and saved")

    @classmethod
    async def _safe_stop(cls):
        """Безопасное отключение клиента"""
        try:
            if cls._client and cls._client.is_connected:
                await cls._client.disconnect()
        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")

    @classmethod
    async def wait_ready(cls):
        """Ожидание готовности клиента"""
        await cls._auth_event.wait()

    @classmethod
    async def get_client(cls):
        """Получение клиента с ожиданием инициализации"""
        await cls.wait_ready()
        return cls._client
