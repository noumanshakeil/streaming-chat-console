"""LLM provider factory."""
from backend.config import settings
from backend.llm.base import LLMProvider
from backend.llm.mock import MockLLM
from backend.llm.ollama import OllamaLLM
from backend.llm.openai_provider import OpenAILLM


def get_llm() -> LLMProvider:
    mode = (settings.llm_mode or "mock").lower()
    if mode == "openai" and settings.openai_api_key:
        return OpenAILLM()
    if mode == "ollama":
        return OllamaLLM()
    return MockLLM()
