from __future__ import annotations

import hashlib

import httpx

from .config import settings


def complete(prompt: str) -> str:
    mode = (settings.llm_mode or "mock").lower()
    if mode == "openai" and settings.openai_api_key:
        return _openai(prompt)
    if mode == "ollama":
        return _ollama(prompt)
    return _mock(prompt)


def _mock(prompt: str) -> str:
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:10]
    snippet = " ".join(prompt.split())[:180]
    return (
        f"[mock-llm:{digest}] Draft response based on: {snippet}. "
        "Replace LLM_MODE with openai or ollama for live models."
    )


def _openai(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a precise full-stack AI assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    with httpx.Client(timeout=60) as client:
        r = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


def _ollama(prompt: str) -> str:
    body = {"model": settings.ollama_model, "prompt": prompt, "stream": False}
    with httpx.Client(timeout=120) as client:
        r = client.post(f"{settings.ollama_base_url}/api/generate", json=body)
        r.raise_for_status()
        return r.json().get("response", "")
