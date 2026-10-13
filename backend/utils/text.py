from __future__ import annotations
import re

_WS = re.compile(r"\s+")

def normalize(text: str) -> str:
    return _WS.sub(" ", (text or "").strip())

def token_set(text: str) -> set[str]:
    return {t for t in normalize(text).lower().split() if len(t) > 1}
