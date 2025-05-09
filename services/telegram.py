from pyrogram import Client
from pyrogram.errors import (
    SessionPasswordNeeded,
    BadRequest,
    AuthKeyUnregistered,
    FloodWait,
    PhoneNumberInvalid
)
import logging
from core.config import settings
import asyncio
import qrcode
from io import BytesIO
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TelegramService:
    _instance = None
    _client: Optional[Client] = None
    _qr_data: Optional[Dict[str, Any]] = None
    _auth_event = asyncio.Event()
    _last_init_time: Optional[datetime] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def initialize(cls) -> bool:
        """Initialize Telegram client"""
        if await cls._is_connected():
            return True

        try:
            if cls._last_init_time and (datetime.now() - cls._last_init_time) < timedelta(minutes=1):
                logger.warning("Initialization throttled")
                return False

            cls._last_init_time = datetime.now()
            cls._client = Client(
                name="tg_web_client",
                api_id=settings.TELEGRAM_API_ID,
                api_hash=settings.TELEGRAM_API_HASH,
                session_string=settings.SESSION_STRING or None,
                in_memory=True,
                device_model="Telegram Web",
                system_version="FastAPI",
                app_version="1.0"
            )

            if settings.SESSION_STRING:
                await cls._start_client()
                return True

            return False

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            await cls.shutdown()
            raise

    @classmethod
    async def _start_client(cls):
        """Start client with existing session"""
        try:
            await cls._client.start()
            cls._auth_event.set()
            logger.info("Telegram client started successfully")
        except AuthKeyUnregistered:
            logger.warning("Session expired, clearing...")
            settings.SESSION_STRING = None
            await cls.shutdown()
            raise RuntimeError("Session expired, please login again")

    @classmethod
    async def shutdown(cls):
        """Properly shutdown client"""
        try:
            if cls._client and await cls._is_connected():
                await cls._client.stop()
                logger.info("Telegram client stopped")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            cls._client = None
            cls._qr_data = None
            cls._auth_event.clear()

    @classmethod
    async def generate_qr_login(cls) -> Dict[str, str]:
        """Generate QR code for login"""
        if await cls.is_authenticated():
            raise RuntimeError("Already authenticated")

        if not cls._client:
            await cls.initialize()

        try:
            await cls._client.connect()
            qr_login = await cls._client.export_qr_code()

            # Generate QR image
            img = qrcode.make(qr_login.url)
            buffered = BytesIO()
            img.save(buffered, format="PNG", optimize=True)
            qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            cls._qr_data = {
                "qr_code": qr_base64,
                "qr_url": qr_login.url,
                "expires": datetime.now() + timedelta(minutes=2)
            }

            # Start background login waiter
            asyncio.create_task(cls._wait_for_qr_login(qr_login))

            return {
                "qr_code": qr_base64,
                "qr_url": qr_login.url,
                "expires_in": 120  # seconds
            }

        except Exception as e:
            await cls.shutdown()
            logger.error(f"QR generation failed: {e}")
            raise

    @classmethod
    async def _wait_for_qr_login(cls, qr_login):
        """Wait for QR login completion"""
        try:
            await qr_login.wait(timeout=120)
            settings.SESSION_STRING = await cls._client.export_session_string()
            cls._auth_event.set()
            logger.info("QR login successful")
        except asyncio.TimeoutError:
            logger.warning("QR login timed out")
        except Exception as e:
            logger.error(f"QR login failed: {e}")
        finally:
            cls._qr_data = None

    @classmethod
    async def get_client(cls) -> Client:
        """Get active client instance"""
        if not await cls.is_authenticated():
            raise RuntimeError("Not authenticated")

        if not await cls._is_connected():
            await cls._start_client()

        return cls._client

    @classmethod
    async def _is_connected(cls) -> bool:
        """Check connection status"""
        return cls._client and await cls._client.is_connected()

    @classmethod
    async def is_authenticated(cls) -> bool:
        """Check authentication status"""
        return cls._auth_event.is_set()

    @classmethod
    async def is_ready(cls) -> bool:
        """Check if service is ready"""
        return await cls.is_authenticated() and await cls._is_connected()
