from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from services.telegram import TelegramService
import logging
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

# Настройка шаблонов
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=templates_dir)


@router.get("/qr_login", response_class=HTMLResponse)
async def qr_login_page(request: Request):
    """Страница с QR кодом для входа"""
    try:
        qr_code = await TelegramService.get_qr_code()
        return templates.TemplateResponse(
            "qr_login.html",
            {
                "request": request,
                "qr_code": qr_code,
                "refresh_interval": 5000  # 5 секунд
            }
        )
    except RuntimeError as e:
        if "upgrade Pyrogram" in str(e):
            return HTMLResponse(
                content="""
                <h1>Error</h1>
                <p>Please upgrade Pyrogram:</p>
                <pre>pip install --upgrade pyrogram>=2.0.0</pre>
                """,
                status_code=400
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"QR login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def auth_status():
    """Проверка статуса аутентификации"""
    try:
        authenticated = await TelegramService.is_authenticated()
        return JSONResponse(
            status_code=200,
            content={"authenticated": authenticated}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
