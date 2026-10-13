"""Runtime configuration loaded from environment / .env."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "streaming-chat-console"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "sqlite+aiosqlite:///./data/app.db"
    llm_mode: str = "mock"  # mock | openai | ollama
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2"

    log_level: str = "INFO"
    request_timeout_s: float = 60.0
    cors_origins: str = Field(default="*")

    # Domain toggles
    require_approval: bool = True
    dry_run_default: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
