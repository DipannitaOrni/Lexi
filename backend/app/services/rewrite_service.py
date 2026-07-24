"""
Stage 1 — Adaptive Rewriting.
"""
import asyncio
from typing import List

from app.prompts.rewrite_prompts import build_rewrite_user_prompt
from app.prompts.system_prompts import REWRITE_SYSTEM_PROMPT
from app.services.document_store import StoredDocument, document_store
from app.services.gemma_client import call_llm
from app.utils.json_parsing import JsonParseError, parse_json_safely
from app.utils.logging_config import get_logger, log_event, safe_excerpt

logger = get_logger("rewrite_service")

# Bound concurrent LLM calls so we don't blow through rate limits when a
# document has many chunks.
_MAX_CONCURRENT_CALLS = 4


async def _rewrite_single_chunk(
    chunk_text: str, mode: str, chunk_id: str, reading_level: int, semaphore: asyncio.Semaphore
) -> dict:
    user_prompt = build_rewrite_user_prompt(
        chunk_text=chunk_text, mode=mode, chunk_id=chunk_id, reading_level=reading_level
    )

    async with semaphore:
        raw_response = await call_llm(
            system_prompt=REWRITE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.25,
            stage="rewrite",
        )

    try:
        parsed = parse_json_safely(raw_response)
    except JsonParseError:
        log_event(logger, "rewrite_json_parse_retry", level="warning", chunk_id=chunk_id)
        corrected_prompt = user_prompt + "\n\nReminder: return ONLY valid JSON, nothing else."
        async with semaphore:
            raw_response = await call_llm(
                system_prompt=REWRITE_SYSTEM_PROMPT,
                user_prompt=corrected_prompt,
                temperature=0.1,
                stage="rewrite_retry",
            )
        parsed = parse_json_safely(raw_response)

    log_event(
        logger, "rewrite_chunk_complete", chunk_id=chunk_id, mode=mode,
        excerpt=safe_excerpt(parsed.get("rewritten_text", "")),
    )
    return {
        "chunk_id": chunk_id,
        "rewritten_text": parsed.get("rewritten_text", ""),
        "mode": mode,
    }


def _cache_key(mode: str, reading_level: int) -> str:
    return f"{mode}:{reading_level}"


async def rewrite_document(document: StoredDocument, mode: str, reading_level: int = 3) -> List[dict]:
    """
    Rewrites every chunk of `document` for the given accessibility mode and
    reading-level target, running independent chunks concurrently (bounded),
    and returns the list of per-chunk results in original order. Uses the
    cache if this (mode, reading_level) combination was already rewritten.
    """
    key = _cache_key(mode, reading_level)
    if key in document.rewrite_cache:
        log_event(logger, "rewrite_cache_hit", document_id=document.document_id, mode=mode)
        return document.rewrite_cache[key]

    semaphore = asyncio.Semaphore(_MAX_CONCURRENT_CALLS)
    tasks = [
        _rewrite_single_chunk(chunk.text, mode, chunk.chunk_id, reading_level, semaphore)
        for chunk in document.chunks
    ]
    results = await asyncio.gather(*tasks)

    document.rewrite_cache[key] = results
    document_store.save(document)
    return results


async def rewrite_document_streaming(document: StoredDocument, mode: str, reading_level: int = 3):
    """
    Async generator variant of rewrite_document: yields each chunk's result
    as soon as it completes, for the SSE streaming endpoint, instead of
    waiting for the whole document. Chunks still run concurrently.
    """
    key = _cache_key(mode, reading_level)
    if key in document.rewrite_cache:
        for r in document.rewrite_cache[key]:
            yield r
        return

    semaphore = asyncio.Semaphore(_MAX_CONCURRENT_CALLS)
    tasks = {
        asyncio.ensure_future(
            _rewrite_single_chunk(chunk.text, mode, chunk.chunk_id, reading_level, semaphore)
        ): chunk.order
        for chunk in document.chunks
    }

    results_by_order = {}
    for finished in asyncio.as_completed(list(tasks.keys())):
        result = await finished
        order = tasks[finished] if finished in tasks else None
        results_by_order[result["chunk_id"]] = result
        yield result

    # Cache in original chunk order once all are done
    ordered = [results_by_order[c.chunk_id] for c in document.chunks if c.chunk_id in results_by_order]
    document.rewrite_cache[key] = ordered
    document_store.save(document)


def rewritten_chunks_to_full_text(results: List[dict]) -> str:
    return "\n\n".join(r["rewritten_text"] for r in results)
