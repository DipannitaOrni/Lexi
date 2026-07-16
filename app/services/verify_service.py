"""
Stage 2 — Self Verification.

Verification always runs per-chunk against its corresponding original
chunk (never the whole document at once), per design doc Section 6.7 —
this keeps each Gemma call small and reliable.
"""
import asyncio
from typing import List, Optional

from app.prompts.system_prompts import VERIFY_SYSTEM_PROMPT
from app.prompts.verify_prompts import RETRY_WITH_WARNINGS_SUFFIX, build_verify_user_prompt
from app.services.document_store import StoredDocument
from app.services.gemma_client import call_gemma
from app.services.rewrite_service import rewritten_chunks_to_full_text
from app.utils.json_parsing import JsonParseError, parse_json_safely
from app.utils.logging_config import get_logger, log_event

logger = get_logger("verify_service")

CONFIDENCE_THRESHOLD = 0.7
_MAX_CONCURRENT_CALLS = 4


async def _verify_single_chunk(original_text: str, rewritten_text: str, chunk_id: str, semaphore: asyncio.Semaphore) -> dict:
    user_prompt = build_verify_user_prompt(original_text, rewritten_text, chunk_id)

    async with semaphore:
        raw_response = await call_gemma(
            system_prompt=VERIFY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.0,  # verification is a comparison task, not creative — deterministic as possible
            stage="verify",
        )

    try:
        parsed = parse_json_safely(raw_response)
    except JsonParseError:
        log_event(logger, "verify_json_parse_retry", level="warning", chunk_id=chunk_id)
        corrected_prompt = user_prompt + "\n\nReminder: return ONLY valid JSON, nothing else."
        async with semaphore:
            raw_response = await call_gemma(
                system_prompt=VERIFY_SYSTEM_PROMPT,
                user_prompt=corrected_prompt,
                temperature=0.0,
                stage="verify_retry",
            )
        parsed = parse_json_safely(raw_response)

    parsed.setdefault("chunk_id", chunk_id)
    parsed.setdefault("confidence_score", 0.0)
    parsed.setdefault("is_safe", parsed["confidence_score"] >= CONFIDENCE_THRESHOLD)
    parsed.setdefault("warnings", [])
    for w in parsed["warnings"]:
        w.setdefault("chunk_id", chunk_id)

    log_event(
        logger, "verify_chunk_complete", chunk_id=chunk_id,
        confidence_score=parsed["confidence_score"], warning_count=len(parsed["warnings"]),
    )
    return parsed


async def verify_document(
    document: StoredDocument,
    rewritten_results: List[dict],
    mode: str,
) -> dict:
    """
    Verifies each rewritten chunk against its corresponding original chunk.
    Returns an aggregated result: overall confidence (min across chunks,
    since one bad chunk should not be hidden by good ones), is_safe, and
    the concatenated warnings list.
    """
    cache_key = mode
    if cache_key in document.verify_cache:
        chunk_results = document.verify_cache[cache_key]
    else:
        semaphore = asyncio.Semaphore(_MAX_CONCURRENT_CALLS)
        original_by_id = {c.chunk_id: c.text for c in document.chunks}

        tasks = [
            _verify_single_chunk(
                original_text=original_by_id[r["chunk_id"]],
                rewritten_text=r["rewritten_text"],
                chunk_id=r["chunk_id"],
                semaphore=semaphore,
            )
            for r in rewritten_results
        ]
        chunk_results = await asyncio.gather(*tasks)
        document.verify_cache[cache_key] = chunk_results

    if not chunk_results:
        return {"confidence_score": 1.0, "is_safe": True, "warnings": []}

    overall_confidence = min(r["confidence_score"] for r in chunk_results)
    overall_safe = all(r["is_safe"] for r in chunk_results)
    all_warnings = [w for r in chunk_results for w in r["warnings"]]

    return {
        "confidence_score": overall_confidence,
        "is_safe": overall_safe,
        "warnings": all_warnings,
    }


def summarize_warnings(warnings: List[dict]) -> str:
    if not warnings:
        return "None"
    lines = [f"- [{w['type']}] {w['description']}" for w in warnings]
    return "\n".join(lines)
