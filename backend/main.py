"""Streaming Chat Console — FastAPI backend + Jinja UI."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .llm import complete

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "data" / "store.json"
FIELDS = ['title', 'system_prompt']

app = FastAPI(title="Streaming Chat Console", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def load_store() -> dict:
    if not DATA.exists():
        DATA.parent.mkdir(parents=True, exist_ok=True)
        payload = {"sessions": [
  {
    "id": "ss1",
    "title": "General",
    "system_prompt": "Be concise"
  }
]}
        DATA.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return json.loads(DATA.read_text(encoding="utf-8"))


def save_store(store: dict) -> None:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(store, indent=2), encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "streaming-chat-console", "llm_mode": settings.llm_mode}


@app.get("/api/sessions")
def list_items() -> dict:
    store = load_store()
    return {"sessions": store.get("sessions", [])}


@app.post("/api/sessions")
def create_item(payload: dict) -> dict:
    store = load_store()
    item = {"id": uuid.uuid4().hex[:8]}
    for key in FIELDS:
        item[key] = payload.get(key)
    store.setdefault("sessions", []).insert(0, item)
    save_store(store)
    return item


@app.post("/api/chat")
def run_action(payload: dict) -> dict:
    """Send a chat message (mock streamed tokens)."""
    prompt = (
        "You are the AI engine for Streaming Chat Console.\n"
        "Task: Send a chat message (mock streamed tokens).\n"
        f"Input JSON: {json.dumps(payload)[:4000]}"
    )
    text = complete(prompt)
    return {"ok": True, "action": "chat", "result": text, "mode": settings.llm_mode}


@app.get("/", response_class=HTMLResponse)
def home(request: Request, last_result: str | None = None) -> HTMLResponse:
    store = load_store()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Streaming Chat Console",
            "description": "Token-streaming chat console with sessions, system prompts, and provider switching.",
            "resource": "sessions",
            "action": "chat",
            "action_desc": "Send a chat message (mock streamed tokens)",
            "items": store.get("sessions", []),
            "llm_mode": settings.llm_mode,
            "last_result": last_result,
        },
    )


@app.post("/ui/create", response_class=HTMLResponse)
async def ui_create(request: Request) -> HTMLResponse:
    form = await request.form()
    data = {k: form.get(k) for k in FIELDS}
    create_item(data)
    return home(request)


@app.post("/ui/action", response_class=HTMLResponse)
async def ui_action(request: Request, prompt: str = Form("demo")) -> HTMLResponse:
    result = run_action({"prompt": prompt})
    store = load_store()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Streaming Chat Console",
            "description": "Token-streaming chat console with sessions, system prompts, and provider switching.",
            "resource": "sessions",
            "action": "chat",
            "action_desc": "Send a chat message (mock streamed tokens)",
            "items": store.get("sessions", []),
            "llm_mode": settings.llm_mode,
            "last_result": result.get("result"),
        },
    )
