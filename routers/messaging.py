from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.protocol import TelegramMessage, TelegramChat
from services.telegram import TelegramService
from core.security import get_current_user

router = APIRouter()

@router.get("/chats", response_model=List[TelegramChat])
async def get_chats(_=Depends(get_current_user)):
    return await TelegramService().get_chats()

@router.get("/messages/{chat_id}", response_model=List[TelegramMessage])
async def get_messages(chat_id: int, limit: int = 100, _=Depends(get_current_user)):
    return await TelegramService().get_messages(chat_id, limit)

@router.post("/send_message")
async def send_message(chat_id: int, text: str, _=Depends(get_current_user)):
    return await TelegramService().send_message(chat_id, text)