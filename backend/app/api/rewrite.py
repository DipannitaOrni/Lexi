"""
POST /rewrite — runs Stage 1 only for a given document + mode + reading level.
GET  /rewrite/stream — SSE variant, streams each chunk's rewrite as it completes.
"""
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.rewrite_schema import RewriteRequest, RewriteResponse, RewrittenChunk
from app.services.document_store import document_store
from app.services.gemma_client import LLMAPIError, LLMTimeoutError
from app.services.rewrite_service import (
    rewrite_document,
    rewrite_document_streaming,
    rewritten_chunks_to_full_text,
)
from app.utils.json_parsing import JsonParseError
from app.utils.logging_config import get_logger, log_event

router = APIRouter()
logger = get_logger("api.rewrite")


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite(body: RewriteRequest):
    document = document_store.get(body.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    try:
        results = await rewrite_document(document, body.mode, body.reading_level)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "LLM API timed out during rewriting."}})
    except LLMAPIError as exc:
        log_event(logger, "rewrite_llm_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "LLM API call failed."}})
    except JsonParseError as exc:
        log_event(logger, "rewrite_json_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "invalid_model_output", "message": "Model did not return valid JSON."}})

    return RewriteResponse(
        document_id=body.document_id,
        mode=body.mode,
        reading_level=body.reading_level,
        rewritten_text=rewritten_chunks_to_full_text(results),
        chunks=[RewrittenChunk(**r) for r in results],
    )


@router.post("/rewrite/stream")
async def rewrite_stream(body: RewriteRequest):
    document = document_store.get(body.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    total_chunks = len(document.chunks)

    async def event_generator():
        completed = 0
        try:
            async for result in rewrite_document_streaming(document, body.mode, body.reading_level):
                completed += 1
                payload = {
                    "type": "chunk",
                    "chunk_id": result["chunk_id"],
                    "rewritten_text": result["rewritten_text"],
                    "progress": completed,
                    "total": total_chunks,
                }
                yield f"data: {json.dumps(payload)}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except (LLMAPIError, JsonParseError) as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
