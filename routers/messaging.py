from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.protocol import TelegramMessage, TelegramChat
from services.telegram import TelegramService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/chats", response_model=List[TelegramChat])
async def get_chats():
    """Получение списка чатов"""
    try:
        client = await TelegramService.get_client()
        return [chat async for chat in client.get_dialogs()]
    except Exception as e:
        logger.error(f"Get chats error: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/messages/{chat_id}", response_model=List[TelegramMessage])
async def get_messages(chat_id: int, limit: int = 100):
    """Получение сообщений из чата"""
    try:
        client = await TelegramService.get_client()
        return [msg async for msg in client.get_chat_history(chat_id, limit=limit)]
    except Exception as e:
        logger.error(f"Get messages error: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
