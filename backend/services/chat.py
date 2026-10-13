from __future__ import annotations
import asyncio
from collections.abc import AsyncIterator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import ChatMessage, ChatSession, SystemPrompt
from backend.utils.ids import short_id

async def upsert_system_prompt(session: AsyncSession, name: str, body: str) -> SystemPrompt:
    row = (
        await session.execute(select(SystemPrompt).where(SystemPrompt.name == name))
    ).scalar_one_or_none()
    if row:
        row.body = body.strip()
    else:
        row = SystemPrompt(id=short_id(), name=name.strip()[:120], body=body.strip())
        session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

async def list_system_prompts(session: AsyncSession) -> list[SystemPrompt]:
    return list((await session.execute(select(SystemPrompt).order_by(SystemPrompt.name))).scalars())

async def create_session(
    session: AsyncSession,
    title: str,
    system_prompt_id: str | None = None,
    system_inline: str = "",
) -> ChatSession:
    chat = ChatSession(
        id=short_id(),
        title=title.strip()[:200] or "New chat",
        system_prompt_id=system_prompt_id,
        system_inline=system_inline.strip(),
    )
    session.add(chat)
    await session.commit()
    await session.refresh(chat)
    return chat

async def list_sessions(session: AsyncSession) -> list[ChatSession]:
    return list(
        (await session.execute(select(ChatSession).order_by(ChatSession.created_at.desc()))).scalars()
    )

async def get_messages(session: AsyncSession, session_id: str) -> list[ChatMessage]:
    stmt = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    return list((await session.execute(stmt)).scalars())

async def _system_text(session: AsyncSession, chat: ChatSession) -> str:
    if chat.system_inline:
        return chat.system_inline
    if chat.system_prompt_id:
        sp = await session.get(SystemPrompt, chat.system_prompt_id)
        if sp:
            return sp.body
    return "You are a helpful assistant."

async def send_message(session: AsyncSession, session_id: str, content: str) -> dict:
    chat = await session.get(ChatSession, session_id)
    if not chat:
        raise ValueError("session not found")
    user = ChatMessage(id=short_id(), session_id=session_id, role="user", content=content.strip())
    session.add(user)
    await session.flush()
    history = await get_messages(session, session_id)
    transcript = "\n".join(f"{m.role}: {m.content}" for m in history[-12:])
    system = await _system_text(session, chat)
    llm = get_llm()
    reply = await llm.complete(
        f"Continue the conversation.\n\n{transcript}\nassistant:",
        system=system,
    )
    assistant = ChatMessage(id=short_id(), session_id=session_id, role="assistant", content=reply)
    session.add(assistant)
    await session.commit()
    return {"user_id": user.id, "assistant_id": assistant.id, "reply": reply}

async def stream_reply(session: AsyncSession, session_id: str, content: str) -> AsyncIterator[str]:
    chat = await session.get(ChatSession, session_id)
    if not chat:
        raise ValueError("session not found")
    user = ChatMessage(id=short_id(), session_id=session_id, role="user", content=content.strip())
    session.add(user)
    await session.flush()
    history = await get_messages(session, session_id)
    transcript = "\n".join(f"{m.role}: {m.content}" for m in history[-12:])
    system = await _system_text(session, chat)
    llm = get_llm()
    full = await llm.complete(
        f"Continue the conversation.\n\n{transcript}\nassistant:",
        system=system,
    )
    chunks = [full[i : i + 24] for i in range(0, max(len(full), 1), 24)] or [full]
    acc = ""
    for piece in chunks:
        acc += piece
        yield piece
        await asyncio.sleep(0.01)
    assistant = ChatMessage(id=short_id(), session_id=session_id, role="assistant", content=acc)
    session.add(assistant)
    await session.commit()
