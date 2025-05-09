from pyrogram import Client
from pyrogram.types import Message, Chat
from typing import List, Optional
import logging
from core.config import settings

class TelegramService:
    _client: Optional[Client] = None

    @classmethod
    async def init(cls):
        if settings.SESSION_STRING:
            cls._client = Client(
                "tg-web-session",
                api_id=settings.TELEGRAM_API_ID,
                api_hash=settings.TELEGRAM_API_HASH,
                session_string=settings.SESSION_STRING
            )
            await cls._client.start()

    async def send_code(self, phone_number: str):
        if not self._client:
            self._client = Client("tg-web", api_id=settings.TELEGRAM_API_ID, api_hash=settings.TELEGRAM_API_HASH)
            await self._client.connect()
        return await self._client.send_code(phone_number)

    async def sign_in(self, phone_number: str, code: str):
        await self._client.sign_in(phone_number, code)
        return await self._client.export_session_string()

    async def get_chats(self) -> List[Chat]:
        return [dialog.chat async for dialog in self._client.get_dialogs()]

    async def get_messages(self, chat_id: int, limit: int = 100) -> List[Message]:
        return [message async for message in self._client.get_chat_history(chat_id, limit=limit)]

    async def send_message(self, chat_id: int, text: str):
        return await self._client.send_message(chat_id, text)