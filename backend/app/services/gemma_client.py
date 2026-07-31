"""
Single wrapper around Gemma models hosted on Google's Gemini API (Google AI
Studio). Every LLM call in the system goes through this module — no other
file should talk to the inference backend directly.

Provides the same four capabilities used across the pipeline, with the
exact same function signatures as the previous OpenAI-based client:
- call_llm()         — chat completion (Stages 1/2/3, flashcards, key points)
- get_embedding()     — text embeddings (Stage 3 semantic retrieval)
- transcribe_audio()  — speech-to-text (voice question input in ChatBox)

Backend: cloud, API-key based, no local server/GPU required — get a key at
https://aistudio.google.com/apikey and set GEMMA_API_KEY.

Model choices and honest limitations:
- Chat runs on a real hosted Gemma 4 model (default: gemma-4-31b-it).
- Speech-to-text uses gemma-4-12b-it, the one Gemma 4 size whose native
  audio-input capability is currently exposed through the hosted API (the
  smaller E2B/E4B audio-capable builds are edge/on-device only, not hosted).
- Embeddings and text-to-speech: Gemma has NO hosted embedding model and NO
  audio-output capability at all (it can listen, not speak). There is no
  Gemma way to satisfy these two features, so they fall back to Gemini
  models on the same API/key (gemini-embedding-001, gemini-3.1-flash-tts-
  preview respectively). These two are the only non-Gemma pieces in this
  file — see the migration summary for details.

Includes async, non-blocking calls, configurable timeout, exponential-
backoff retry on transient failures (5xx, timeouts, rate limits), no retry
on other 4xx errors, and structured logging of latency — never logging the
API key.
"""
import asyncio
import base64
import struct
import subprocess
import time
from typing import List, Optional

import httpx

from app.config import get_settings
from app.utils.logging_config import get_logger, log_event

logger = get_logger("gemma_client")


class LLMAPIError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class LLMTimeoutError(LLMAPIError):
    pass


def _require_key(settings) -> str:
    if not settings.gemma_api_key:
        raise LLMAPIError("GEMMA_API_KEY is not configured")
    return settings.gemma_api_key


def _headers(api_key: str) -> dict:
    return {"Content-Type": "application/json", "x-goog-api-key": api_key}


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    stage: str = "unknown",
) -> str:
    """Calls the hosted Gemma chat model and returns the raw text response."""
    settings = get_settings()
    api_key = _require_key(settings)
    url = f"{settings.gemma_api_base}/models/{settings.gemma_chat_model}:generateContent"
    last_error: Optional[Exception] = None

    for attempt in range(1, settings.llm_max_retries + 1):
        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                response = await client.post(
                    url,
                    headers=_headers(api_key),
                    json={
                        "systemInstruction": {"parts": [{"text": system_prompt}]},
                        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                        "generationConfig": {
                            "temperature": temperature,
                            # NOTE: responseMimeType/"application/json" is intentionally NOT set here.
                            # Gemma models (unlike Gemini) reject it with a 400 "JSON mode is not
                            # enabled for this model" error, which made /health falsely report
                            # llm_api: "unreachable". Structured output is instead enforced via the
                            # system prompt + app/utils/json_parsing.parse_json_safely(), which already
                            # strips markdown fences / extracts the {...} span as a fallback.
                        },
                    },
                )
            latency_ms = round((time.monotonic() - start) * 1000, 1)

            if response.status_code == 429:
                last_error = LLMAPIError(f"Gemma API rate limit: {response.text[:200]}", 429)
                log_event(logger, "llm_call_rate_limited", level="warning", stage=stage, attempt=attempt)
                await asyncio.sleep(2 ** attempt)
                continue

            if response.status_code >= 500:
                last_error = LLMAPIError(f"Gemma API server error: {response.status_code}", response.status_code)
                log_event(logger, "llm_call_retry", level="warning", stage=stage, attempt=attempt, status_code=response.status_code)
                await asyncio.sleep(2 ** (attempt - 1))
                continue

            if response.status_code >= 400:
                log_event(logger, "llm_call_client_error", level="error", stage=stage, status_code=response.status_code)
                raise LLMAPIError(f"Gemma API client error: {response.status_code} {response.text[:200]}", response.status_code)

            data = response.json()
            text = _extract_text(data)
            log_event(logger, "llm_call_end", stage=stage, attempt=attempt, latency_ms=latency_ms)
            return text

        except httpx.TimeoutException:
            latency_ms = round((time.monotonic() - start) * 1000, 1)
            last_error = LLMTimeoutError(f"Gemma API timeout after {latency_ms}ms")
            log_event(logger, "llm_call_timeout", level="warning", stage=stage, attempt=attempt, latency_ms=latency_ms)
            await asyncio.sleep(2 ** (attempt - 1))
            continue

    log_event(logger, "llm_call_failed_all_retries", level="error", stage=stage)
    raise last_error or LLMAPIError("Gemma API call failed for an unknown reason")


def _extract_text(data: dict) -> str:
    try:
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts)
    except (KeyError, IndexError):
        return ""


async def get_embedding(text: str) -> List[float]:
    """
    Returns an embedding vector for `text`.

    LIMITATION: Gemma has no hosted embedding model at all, so this calls
    Gemini's embedding model (gemini-embedding-001) on the same API/key
    instead. This is the one non-Gemma model used purely out of necessity —
    see migration summary.
    """
    settings = get_settings()
    api_key = _require_key(settings)
    url = f"{settings.gemma_api_base}/models/{settings.gemma_embedding_model}:embedContent"
    last_error: Optional[Exception] = None

    for attempt in range(1, settings.llm_max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                response = await client.post(
                    url,
                    headers=_headers(api_key),
                    json={"content": {"parts": [{"text": text[:8000]}]}},  # guard oversized single-chunk input
                )
            if response.status_code == 429:
                last_error = LLMAPIError("Gemma embeddings rate limited", 429)
                await asyncio.sleep(2 ** attempt)
                continue
            if response.status_code >= 500:
                last_error = LLMAPIError(f"Gemma embeddings server error: {response.status_code}", response.status_code)
                await asyncio.sleep(2 ** (attempt - 1))
                continue
            if response.status_code >= 400:
                raise LLMAPIError(f"Gemma embeddings client error: {response.status_code} {response.text[:200]}", response.status_code)

            data = response.json()
            values = (data.get("embedding") or {}).get("values")
            if not values:
                raise LLMAPIError("Gemma embeddings response contained no vector")
            return values

        except httpx.TimeoutException:
            last_error = LLMTimeoutError("Gemma embeddings timeout")
            await asyncio.sleep(2 ** (attempt - 1))
            continue

    raise last_error or LLMAPIError("Gemma embeddings call failed")


def _pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 24000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
    """Wraps raw 16-bit PCM (as returned by Gemini TTS) in a minimal WAV header."""
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    data_size = len(pcm_bytes)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + data_size, b"WAVE", b"fmt ", 16, 1, channels,
        sample_rate, byte_rate, block_align, bits_per_sample, b"data", data_size,
    )
    return header + pcm_bytes


def _wav_to_mp3(wav_bytes: bytes) -> bytes:
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-f", "wav", "-i", "pipe:0", "-f", "mp3", "pipe:1"],
            input=wav_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
        )
        if result.returncode != 0 or not result.stdout:
            raise LLMAPIError(f"ffmpeg mp3 transcoding failed: {result.stderr[:200]}")
        return result.stdout
    except FileNotFoundError as exc:
        raise LLMAPIError("ffmpeg is not installed. Install it (e.g. `apt-get install ffmpeg`) to enable /tts.") from exc


async def synthesize_speech(text: str, voice: Optional[str] = None, speed: float = 1.0) -> bytes:
    """
    Synthesizes `text` to speech and returns MP3 bytes.

    LIMITATION: Gemma has no audio-output capability at all (it can listen,
    not speak), so this calls Gemini's TTS model (gemini-2.5-flash-preview-tts
    by default) on the same API/key instead — the other non-Gemma piece in
    this file, alongside get_embedding().
    """
    settings = get_settings()
    api_key = _require_key(settings)
    voice_name = voice or settings.gemma_tts_voice
    url = f"{settings.gemma_api_base}/models/{settings.gemma_tts_model}:generateContent"

    prompt = text if speed == 1.0 else f"Say the following at a {speed}x pace: {text}"

    last_error: Optional[Exception] = None
    for attempt in range(1, settings.llm_max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
                response = await client.post(
                    url,
                    headers=_headers(api_key),
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "responseModalities": ["AUDIO"],
                            "speechConfig": {
                                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice_name}}
                            },
                        },
                    },
                )
            if response.status_code == 429:
                last_error = LLMAPIError("Gemma TTS rate limited", 429)
                await asyncio.sleep(2 ** attempt)
                continue
            if response.status_code >= 500:
                last_error = LLMAPIError(f"Gemma TTS server error: {response.status_code}", response.status_code)
                await asyncio.sleep(2 ** (attempt - 1))
                continue
            if response.status_code >= 400:
                raise LLMAPIError(f"Gemma TTS client error: {response.status_code} {response.text[:200]}", response.status_code)

            data = response.json()
            try:
                inline = data["candidates"][0]["content"]["parts"][0]["inlineData"]
                pcm_bytes = base64.b64decode(inline["data"])
            except (KeyError, IndexError) as exc:
                raise LLMAPIError("Gemma TTS response contained no audio") from exc

            wav_bytes = _pcm_to_wav(pcm_bytes)
            return _wav_to_mp3(wav_bytes)

        except httpx.TimeoutException:
            last_error = LLMTimeoutError("Gemma TTS timeout")
            await asyncio.sleep(2 ** (attempt - 1))
            continue

    raise last_error or LLMAPIError("Gemma TTS call failed")


async def transcribe_audio(file_bytes: bytes, filename: str) -> str:
    """
    Transcribes spoken audio to text using Gemma's native audio-input (ASR)
    capability (gemma-4-12b-it), sent as inline audio data to generateContent.
    """
    settings = get_settings()
    api_key = _require_key(settings)
    url = f"{settings.gemma_api_base}/models/{settings.gemma_asr_model}:generateContent"

    ext = (filename.rsplit(".", 1)[-1] if "." in filename else "webm").lower()
    mime_map = {"mp3": "audio/mp3", "wav": "audio/wav", "webm": "audio/webm", "ogg": "audio/ogg", "m4a": "audio/mp4"}
    mime_type = mime_map.get(ext, "audio/webm")

    prompt = (
        "Transcribe the following speech segment into text. "
        "Only output the transcription, with no extra commentary, quotes, or newlines."
    )

    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(
                url,
                headers=_headers(api_key),
                json={
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {"inlineData": {"mimeType": mime_type, "data": base64.b64encode(file_bytes).decode("ascii")}},
                        ]
                    }]
                },
            )
    except httpx.TimeoutException:
        raise LLMTimeoutError("Gemma transcription timeout")

    if response.status_code >= 400:
        raise LLMAPIError(
            f"Gemma transcription error: {response.status_code} {response.text[:200]} "
            f"(check that {settings.gemma_asr_model} supports hosted audio input)",
            response.status_code,
        )

    data = response.json()
    return _extract_text(data).strip()
