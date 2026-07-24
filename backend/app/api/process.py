"""
POST /process — convenience orchestration endpoint: runs Stage 1 then
Stage 2 in one call, plus computes before/after readability stats
(StatsRow.jsx).

Fallback strategy: if verification confidence is below threshold,
automatically retry Stage 1 once for the low-confidence chunks with the
specific warnings appended as extra constraints. If the retry still scores
low, the rewrite is still returned to the user WITH the warnings attached.

Partial-failure handling: if Stage 1 succeeds but Stage 2 fails/times out,
the rewrite is still returned with verification=null and
verification_error set, rather than failing the whole request.
"""
import asyncio

from fastapi import APIRouter, HTTPException

from app.prompts.rewrite_prompts import build_rewrite_user_prompt
from app.prompts.system_prompts import REWRITE_SYSTEM_PROMPT
from app.schemas.verify_schema import (
    DocumentStats,
    ProcessRequest,
    ProcessResponse,
    ReadabilityStatsModel,
    VerificationWarning,
    VerifyResponse,
)
from app.services.document_store import document_store
from app.services.gemma_client import LLMAPIError, LLMTimeoutError, call_llm
from app.services.rewrite_service import rewrite_document, rewritten_chunks_to_full_text
from app.services.verify_service import CONFIDENCE_THRESHOLD, summarize_warnings, verify_document
from app.utils.json_parsing import JsonParseError, parse_json_safely
from app.utils.logging_config import get_logger, log_event
from app.utils.readability import compute_readability

router = APIRouter()
logger = get_logger("api.process")


async def _retry_rewrite_chunk_with_warnings(document, mode: str, reading_level: int, chunk_id: str, warnings: list) -> dict:
    chunk = next(c for c in document.chunks if c.chunk_id == chunk_id)
    base_prompt = build_rewrite_user_prompt(chunk_text=chunk.text, mode=mode, chunk_id=chunk_id, reading_level=reading_level)
    warnings_for_chunk = [w for w in warnings if w.get("chunk_id") == chunk_id]
    reminder = "\n\nIMPORTANT: a previous attempt had these issues, do not repeat them:\n" + summarize_warnings(warnings_for_chunk)

    raw_response = await call_llm(
        system_prompt=REWRITE_SYSTEM_PROMPT,
        user_prompt=base_prompt + reminder,
        temperature=0.1,
        stage="rewrite_confidence_retry",
    )
    parsed = parse_json_safely(raw_response)
    return {"chunk_id": chunk_id, "rewritten_text": parsed.get("rewritten_text", ""), "mode": mode}


@router.post("/process", response_model=ProcessResponse)
async def process(body: ProcessRequest):
    document = document_store.get(body.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    cache_key = f"{body.mode}:{body.reading_level}"

    try:
        rewritten_results = await rewrite_document(document, body.mode, body.reading_level)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "LLM API timed out during rewriting."}})
    except (LLMAPIError, JsonParseError) as exc:
        log_event(logger, "process_rewrite_failed", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "rewrite_failed", "message": str(exc)}})

    verification = None
    verification_error = None
    try:
        verify_result = await verify_document(document, rewritten_results, cache_key)

        if verify_result["confidence_score"] < CONFIDENCE_THRESHOLD:
            log_event(
                logger, "process_low_confidence_retry", level="warning",
                document_id=body.document_id, confidence=verify_result["confidence_score"],
            )
            low_conf_chunk_ids = {w["chunk_id"] for w in verify_result["warnings"]}
            retried = await asyncio.gather(*[
                _retry_rewrite_chunk_with_warnings(document, body.mode, body.reading_level, cid, verify_result["warnings"])
                for cid in low_conf_chunk_ids
            ])
            retried_by_id = {r["chunk_id"]: r for r in retried}
            rewritten_results = [retried_by_id.get(r["chunk_id"], r) for r in rewritten_results]
            document.rewrite_cache[cache_key] = rewritten_results
            document.verify_cache.pop(cache_key, None)
            document_store.save(document)
            verify_result = await verify_document(document, rewritten_results, cache_key)

        verification = VerifyResponse(
            document_id=body.document_id,
            confidence_score=verify_result["confidence_score"],
            is_safe=verify_result["is_safe"],
            warnings=[VerificationWarning(**w) for w in verify_result["warnings"]],
        )
    except LLMTimeoutError:
        verification_error = "llm_timeout_during_verification"
    except (LLMAPIError, JsonParseError) as exc:
        log_event(logger, "process_verify_failed", level="error", error=str(exc))
        verification_error = "verification_failed"

    rewritten_text = rewritten_chunks_to_full_text(rewritten_results)

    original_stats = compute_readability(document.preprocessed_text)
    rewritten_stats = compute_readability(rewritten_text)
    stats = DocumentStats(
        original=ReadabilityStatsModel(**original_stats.__dict__),
        rewritten=ReadabilityStatsModel(**rewritten_stats.__dict__),
    )

    return ProcessResponse(
        document_id=body.document_id,
        mode=body.mode,
        reading_level=body.reading_level,
        rewritten_text=rewritten_text,
        verification=verification,
        verification_error=verification_error,
        stats=stats,
    )
