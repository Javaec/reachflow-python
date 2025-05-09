from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


class TelegramChat(BaseModel):
    id: int
    type: str  # "private", "group", "supergroup" or "channel"
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TelegramMessage(BaseModel):
    id: int
    chat: TelegramChat
    from_user: Optional[TelegramUser] = None
    text: Optional[str] = None
    date: datetime

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.timestamp()
        }
    )
