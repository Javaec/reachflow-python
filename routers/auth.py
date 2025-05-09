from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.telegram import TelegramService
import logging
from pathlib import Path
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# Setup templates
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=templates_dir)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Main login page with QR code"""
    try:
        # Check if already authenticated
        if await TelegramService.is_authenticated():
            return RedirectResponse(url="/")

        # Generate new QR code
        qr_data = await TelegramService.generate_qr_login()

        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "qr_code": qr_data["qr_code"],
                "qr_url": qr_data["qr_url"],
                "expires_in": qr_data["expires_in"],
                "refresh_interval": 3000  # 3 seconds
            }
        )
    except Exception as e:
        logger.error(f"Login page error: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/auth/status", response_class=JSONResponse)
async def auth_status():
    """Authentication status endpoint"""
    try:
        return {
            "authenticated": await TelegramService.is_authenticated(),
            "ready": await TelegramService.is_ready()
        }
    except Exception as e:
        logger.error(f"Auth status error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/logout", response_class=JSONResponse)
async def logout():
    """Logout and clear session"""
    try:
        await TelegramService.shutdown()
        return {"status": "success", "message": "Logged out"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/session", response_class=JSONResponse)
async def get_session_info():
    """Get current session info"""
    try:
        if await TelegramService.is_authenticated():
            client = await TelegramService.get_client()
            me = await client.get_me()
            return {
                "user": {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username,
                    "phone_number": me.phone_number
                }
            }
        return {"authenticated": False}
    except Exception as e:
        logger.error(f"Session info error: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
