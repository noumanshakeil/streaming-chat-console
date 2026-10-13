from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import chat as svc

class SystemPromptIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    body: str = Field(min_length=4)

class SessionIn(BaseModel):
    title: str = "New chat"
    system_prompt_id: str | None = None
    system_inline: str = ""

class MessageIn(BaseModel):
    content: str = Field(min_length=1)

router = APIRouter()

@router.get("/system-prompts")
async def list_prompts(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_system_prompts(db)
    return {"prompts": [{"id": p.id, "name": p.name, "body": p.body[:200]} for p in rows]}

@router.post("/system-prompts")
async def save_prompt(payload: SystemPromptIn, db: AsyncSession = Depends(get_db)):
    row = await svc.upsert_system_prompt(db, payload.name, payload.body)
    return {"id": row.id, "name": row.name}

@router.get("/sessions")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_sessions(db)
    return {"sessions": [{"id": s.id, "title": s.title, "created_at": s.created_at.isoformat()} for s in rows]}

@router.post("/sessions")
async def create_session(payload: SessionIn, db: AsyncSession = Depends(get_db)):
    row = await svc.create_session(db, payload.title, payload.system_prompt_id, payload.system_inline)
    return {"id": row.id, "title": row.title}

@router.get("/sessions/{session_id}/messages")
async def messages(session_id: str, db: AsyncSession = Depends(get_db)):
    msgs = await svc.get_messages(db, session_id)
    return {
        "messages": [
            {"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in msgs
        ]
    }

@router.post("/sessions/{session_id}/messages")
async def post_message(session_id: str, payload: MessageIn, db: AsyncSession = Depends(get_db)):
    try:
        return await svc.send_message(db, session_id, payload.content)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

@router.post("/sessions/{session_id}/stream")
async def stream_message(session_id: str, payload: MessageIn, db: AsyncSession = Depends(get_db)):
    try:
        gen = svc.stream_reply(db, session_id, payload.content)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

    async def event_stream():
        async for chunk in gen:
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
