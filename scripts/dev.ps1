# Dev server for streaming-chat-console
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
