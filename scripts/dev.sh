#!/usr/bin/env bash
set -euo pipefail
export LLM_MODE=mock
exec uvicorn backend.main:app --reload --port 8000
