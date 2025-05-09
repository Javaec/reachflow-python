from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel  # Добавлен импорт BaseModel
from core.security import create_access_token
from core.config import settings
from services.telegram import TelegramService

router = APIRouter()


# Модель для ответа с токеном
class Token(BaseModel):
    access_token: str
    token_type: str


# Модель для запроса авторизации
class AuthRequest(BaseModel):
    phone_number: str


@router.post("/request_code")
async def request_code(request: AuthRequest):
    """Запрос кода подтверждения Telegram"""
    return await TelegramService().send_code(request.phone_number)


@router.post("/sign_in")
async def sign_in(code: str, phone_number: str):
    """Вход с кодом подтверждения"""
    try:
        session_string = await TelegramService().sign_in(phone_number, code)
        return {"status": "success", "session": session_string}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Получение JWT токена для доступа к API"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
