from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import chat as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, session_id: str | None = None, db: AsyncSession = Depends(get_db)):
    sessions = await svc.list_sessions(db)
    messages = await svc.get_messages(db, session_id) if session_id else []
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Streaming Chat Console",
            "sessions": sessions,
            "session_id": session_id,
            "messages": messages,
            "prompts": await svc.list_system_prompts(db),
        },
    )

@router.post("/ui/sessions")
async def ui_session(title: str = Form("New chat"), system_inline: str = Form(""), db: AsyncSession = Depends(get_db)):
    row = await svc.create_session(db, title, system_inline=system_inline)
    return RedirectResponse(f"/?session_id={row.id}", status_code=303)

@router.post("/ui/message")
async def ui_message(session_id: str = Form(...), content: str = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.send_message(db, session_id, content)
    return RedirectResponse(f"/?session_id={session_id}", status_code=303)
