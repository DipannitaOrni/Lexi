"""
Centralized application configuration.
All secrets and tunables are loaded from environment variables (.env in dev,
platform env vars in production) — never hardcoded.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Gemma via the hosted Gemini API (Google AI Studio) — cloud, API-key based,
    # no local server or GPU needed. Get a key at https://aistudio.google.com/apikey
    gemma_api_key: str = ""
    gemma_api_base: str = "https://generativelanguage.googleapis.com/v1beta"
    gemma_chat_model: str = "gemma-4-31b-it"
    # Audio-capable Gemma variant (used for /transcribe). Only the 12B "unified"
    # build is currently exposed with audio input through the hosted API.
    gemma_asr_model: str = "gemma-4-12b-it"
    # Gemma has no cloud-hosted embedding or TTS model at all — these two
    # fall back to Gemini (not Gemma) models on the same API/key. Flagged
    # clearly here and in the migration notes.
    gemma_embedding_model: str = "gemini-embedding-001"
    gemma_tts_model: str = "gemini-2.5-flash-preview-tts"
    gemma_tts_voice: str = "Kore"
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3

    # App
    max_file_size_mb: int = 20
    rate_limit_per_minute: int = 30
    allowed_origins: str = "http://localhost:3000"
    log_level: str = "INFO"

    # Chunking / context budget
    llm_context_window: int = 16000
    prompt_overhead_tokens: int = 500
    response_reserve_tokens: int = 1200

    # Storage
    database_path: str = "./lexi.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def usable_input_tokens(self) -> int:
        budget = self.llm_context_window - self.prompt_overhead_tokens - self.response_reserve_tokens
        return max(budget, 500)


@lru_cache
def get_settings() -> Settings:
    return Settings()
