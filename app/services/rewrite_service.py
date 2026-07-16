"""
Stage 1 — Adaptive Rewriting.
"""
import asyncio
from typing import List

from app.prompts.rewrite_prompts import build_rewrite_user_prompt
from app.prompts.system_prompts import REWRITE_SYSTEM_PROMPT
from app.services.document_store import StoredDocument
from app.services.gemma_client import call_gemma
from app.utils.json_parsing import JsonParseError, parse_json_safely
from app.utils.logging_config import get_logger, log_event, safe_excerpt

logger = get_logger("rewrite_service")

# Bound concurrent Gemma calls so we don't blow through rate limits when a
# document has many chunks.
_MAX_CONCURRENT_CALLS = 4


async def _rewrite_single_chunk(chunk_text: str, mode: str, chunk_id: str, semaphore: asyncio.Semaphore) -> dict:
    user_prompt = build_rewrite_user_prompt(chunk_text=chunk_text, mode=mode, chunk_id=chunk_id)

    async with semaphore:
        raw_response = await call_gemma(
            system_prompt=REWRITE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.25,
            stage="rewrite",
        )

    try:
        parsed = parse_json_safely(raw_response)
    except JsonParseError:
        # One retry with an explicit correction reminder
        log_event(logger, "rewrite_json_parse_retry", level="warning", chunk_id=chunk_id)
        corrected_prompt = user_prompt + "\n\nReminder: return ONLY valid JSON, nothing else."
        async with semaphore:
            raw_response = await call_gemma(
                system_prompt=REWRITE_SYSTEM_PROMPT,
                user_prompt=corrected_prompt,
                temperature=0.1,
                stage="rewrite_retry",
            )
        parsed = parse_json_safely(raw_response)  # let this raise if it fails again

    log_event(
        logger, "rewrite_chunk_complete", chunk_id=chunk_id, mode=mode,
        excerpt=safe_excerpt(parsed.get("rewritten_text", "")),
    )
    return {
        "chunk_id": chunk_id,
        "rewritten_text": parsed.get("rewritten_text", ""),
        "mode": mode,
    }


async def rewrite_document(document: StoredDocument, mode: str) -> List[dict]:
    """
    Rewrites every chunk of `document` for the given accessibility mode,
    running independent chunks concurrently (bounded), and returns the list
    of per-chunk results in original order. Uses the cache if this mode has
    already been rewritten for this document.
    """
    if mode in document.rewrite_cache:
        log_event(logger, "rewrite_cache_hit", document_id=document.document_id, mode=mode)
        return document.rewrite_cache[mode]

    semaphore = asyncio.Semaphore(_MAX_CONCURRENT_CALLS)
    tasks = [
        _rewrite_single_chunk(chunk.text, mode, chunk.chunk_id, semaphore)
        for chunk in document.chunks
    ]
    results = await asyncio.gather(*tasks)

    # asyncio.gather preserves order of the input task list, which matches
    # document.chunks order (already sorted by `order` at chunk time).
    document.rewrite_cache[mode] = results
    return results


def rewritten_chunks_to_full_text(results: List[dict]) -> str:
    return "\n\n".join(r["rewritten_text"] for r in results)
