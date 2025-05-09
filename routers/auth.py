from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel
from core.config import settings
from core.security import create_access_token
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
async def sign_in(code: str, phone_number: str):
    try:
        session_string = await TelegramService().sign_in(phone_number, code)
        return {"status": "success", "session": session_string}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate credentials and return JWT
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}