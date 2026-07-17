"""
Centralized application configuration.
All secrets and tunables are loaded from environment variables (.env in dev,
platform env vars in production) — never hardcoded.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Gemma 4 API
    gemma_api_key: str = "AQ.Ab8RN6KMOjjgydDW3t8ZX3skCOzqL2sbDEJlGO2xbwfiwzaeeQ"
    gemma_api_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    gemma_model_name: str = "gemma-4-26b-a4b-it"
    gemma_timeout_seconds: float = 30.0
    gemma_max_retries: int = 3

    # App
    max_file_size_mb: int = 20
    rate_limit_per_minute: int = 30
    allowed_origins: str = "http://localhost:3000"
    log_level: str = "INFO"

    # Chunking / context budget
    gemma_context_window: int = 8000
    prompt_overhead_tokens: int = 500
    response_reserve_tokens: int = 1200

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def usable_input_tokens(self) -> int:
        budget = self.gemma_context_window - self.prompt_overhead_tokens - self.response_reserve_tokens
        return max(budget, 500)  # never let chunk budget collapse to near-zero


@lru_cache
def get_settings() -> Settings:
    return Settings()
