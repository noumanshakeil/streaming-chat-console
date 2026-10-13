from __future__ import annotations

import hashlib
import json
from typing import Any

from backend.llm.base import LLMProvider


class MockLLM(LLMProvider):
    """Deterministic offline provider for CI / local demos."""

    name = "mock"

    async def complete(self, prompt: str, *, system: str | None = None, temperature: float = 0.2) -> str:
        digest = hashlib.sha256((system or "").encode() + prompt.encode()).hexdigest()[:12]
        snippet = " ".join(prompt.split())[:220]
        return (
            f"[mock:{digest}] {snippet} "
            "| Set LLM_MODE=openai or ollama for live inference."
        )

    async def complete_json(self, prompt: str, *, system: str | None = None) -> dict[str, Any]:
        # Domain-agnostic structured stub — services refine further.
        lower = prompt.lower()
        if "tool" in lower or "plan" in lower:
            return {
                "plan": [
                    {"tool": "run_healthcheck", "args": {"target": "api"}, "rationale": "verify before mutate"},
                    {"tool": "fetch_logs", "args": {"target": "api", "lines": 50}, "rationale": "gather evidence"},
                ],
                "risk": "low",
                "summary": "Mock plan generated offline.",
            }
        if "triage" in lower or "ticket" in lower:
            return {
                "priority": "high",
                "category": "auth",
                "macros": ["reset_mfa", "send_status"],
                "reply": "Thanks for reporting this — we are investigating login failures now.",
                "sla_hours": 4,
            }
        if "brief" in lower or "research" in lower:
            return {
                "title": "Research brief (mock)",
                "sections": [
                    {"heading": "Executive summary", "bullets": ["Key finding A", "Key finding B"]},
                    {"heading": "Evidence", "bullets": ["Source 1 supports claim X"]},
                ],
                "citations": ["src-1", "src-2"],
            }
        if "slot" in lower or "book" in lower:
            return {
                "suggestions": ["2026-10-15T10:00:00Z", "2026-10-15T14:00:00Z"],
                "message": "Happy to book you in — which slot works?",
            }
        if "enrich" in lower or "lead" in lower:
            return {
                "fields": {
                    "company_size": {"value": "51-200", "confidence": 0.72},
                    "industry": {"value": "Software", "confidence": 0.81},
                    "hq_country": {"value": "PK", "confidence": 0.55},
                },
                "notes": "Mock enrichment from public signals.",
            }
        return {"raw": await self.complete(prompt, system=system)}
