from __future__ import annotations

import httpx

from backend.config import settings
from backend.llm.base import LLMProvider


class OllamaLLM(LLMProvider):
    name = "ollama"

    async def complete(self, prompt: str, *, system: str | None = None, temperature: float = 0.2) -> str:
        full = f"System: {system}\n\n{prompt}" if system else prompt
        body = {
            "model": settings.ollama_model,
            "prompt": full,
            "stream": False,
            "options": {"temperature": temperature},
        }
        async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
            resp = await client.post(f"{settings.ollama_base_url}/api/generate", json=body)
            resp.raise_for_status()
            return resp.json().get("response", "")
