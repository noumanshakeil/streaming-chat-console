from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def complete(self, prompt: str, *, system: str | None = None, temperature: float = 0.2) -> str:
        raise NotImplementedError

    async def complete_json(self, prompt: str, *, system: str | None = None) -> dict[str, Any]:
        import json
        import re

        raw = await self.complete(prompt, system=system, temperature=0.0)
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            return {"raw": raw}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"raw": raw}
