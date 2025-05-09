from fastapi import APIRouter, Depends, HTTPException, Form
from datetime import timedelta
from pydantic import BaseModel
from core.security import create_access_token
from core.config import settings
from services.telegram import TelegramService

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class AuthRequest(BaseModel):
    phone_number: str


@router.post("/request_code")
async def request_code(request: AuthRequest):
    return await TelegramService().send_code(request.phone_number)


@router.post("/sign_in")
async def sign_in(
        phone_number: str = Form(...),
        code: str = Form(...)
):
    try:
        session_string = await TelegramService().sign_in(phone_number, code)
        return {"status": "success", "session": session_string}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token", response_model=Token)
async def login_for_access_token(
        username: str = Form(...),
        password: str = Form(...)
):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
