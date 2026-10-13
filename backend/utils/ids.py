from __future__ import annotations
import uuid

def short_id(n: int = 10) -> str:
    return uuid.uuid4().hex[:n]
