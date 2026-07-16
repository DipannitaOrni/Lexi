"""
Single wrapper around the Gemma 4 API. Every LLM call in the system goes
through this module — no other file should call httpx directly.

Uses the Google Generative Language API request/response shape
(models/{model}:generateContent), which is how Gemma models are commonly
served via an API key. The base URL and model name are both configurable
via environment variables in case your team's actual Gemma 4 endpoint
differs — only this file needs to change.

Includes:
- async, non-blocking calls (httpx.AsyncClient)
- configurable timeout
- exponential-backoff retry on transient failures (5xx, timeouts, network errors)
- no retry on 4xx (client errors won't fix themselves)
- structured logging of latency and outcome, never logging the API key
"""
import asyncio
import time
from typing import Optional

import httpx

from app.config import get_settings
from app.utils.logging_config import get_logger, log_event

logger = get_logger("gemma_client")


class GemmaAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GemmaTimeoutError(GemmaAPIError):
    pass


async def call_gemma(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    stage: str = "unknown",
) -> str:
    """
    Calls the Gemma 4 API and returns the raw text response.
    Raises GemmaTimeoutError or GemmaAPIError on failure after retries.
    """
    settings = get_settings()

    if not settings.gemma_api_key:
        raise GemmaAPIError("GEMMA_API_KEY is not configured")

    url = (
        f"{settings.gemma_api_base_url}/models/{settings.gemma_model_name}:generateContent"
        f"?key={settings.gemma_api_key}"
    )

    payload = {
    "system_instruction": {"parts": [{"text": system_prompt}]},
    "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
    "generationConfig": {
        "temperature": temperature,
       
    },
}
    last_error: Optional[Exception] = None

    for attempt in range(1, settings.gemma_max_retries + 1):
        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=settings.gemma_timeout_seconds) as client:
                response = await client.post(url, json=payload)
            latency_ms = round((time.monotonic() - start) * 1000, 1)

            if response.status_code >= 500:
                last_error = GemmaAPIError(
                    f"Gemma API server error: {response.status_code}", response.status_code
                )
                log_event(
                    logger, "gemma_call_retry", level="warning", stage=stage,
                    attempt=attempt, status_code=response.status_code, latency_ms=latency_ms,
                )
                await asyncio.sleep(2 ** (attempt - 1))
                continue

            if response.status_code >= 400:
                # Client error — do not retry
                log_event(
                    logger, "gemma_call_client_error", level="error", stage=stage,
                    status_code=response.status_code, latency_ms=latency_ms,
                )
                raise GemmaAPIError(
                    f"Gemma API client error: {response.status_code} {response.text[:200]}",
                    response.status_code,
                )

            data = response.json()
            text = _extract_text_from_response(data)

            log_event(
                logger, "gemma_call_end", stage=stage, attempt=attempt,
                latency_ms=latency_ms, status_code=response.status_code,
            )
            return text

        except httpx.TimeoutException as exc:
            latency_ms = round((time.monotonic() - start) * 1000, 1)
            last_error = GemmaTimeoutError(f"Gemma API timeout after {latency_ms}ms")
            log_event(
                logger, "gemma_call_timeout", level="warning", stage=stage,
                attempt=attempt, latency_ms=latency_ms,
            )
            await asyncio.sleep(2 ** (attempt - 1))
            continue

        except httpx.HTTPError as exc:
            last_error = GemmaAPIError(f"Gemma API network error: {exc}")
            log_event(logger, "gemma_call_network_error", level="warning", stage=stage, attempt=attempt)
            await asyncio.sleep(2 ** (attempt - 1))
            continue

    log_event(logger, "gemma_call_failed_all_retries", level="error", stage=stage)
    raise last_error or GemmaAPIError("Gemma API call failed for an unknown reason")


def _extract_text_from_response(data: dict) -> str:
    try:
        candidates = data["candidates"]
        parts = candidates[0]["content"]["parts"]

        # Ignore internal reasoning/thought parts and return only the model's answer.
        answer_parts = [
            p.get("text", "")
            for p in parts
            if not p.get("thought", False)
        ]

        return "".join(answer_parts)

    except (KeyError, IndexError, TypeError) as exc:
        raise GemmaAPIError(f"Unexpected Gemma API response shape: {exc}") from exc
