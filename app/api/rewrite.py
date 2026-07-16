"""
POST /rewrite — runs Stage 1 only for a given document + mode.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.rewrite_schema import RewriteRequest, RewriteResponse, RewrittenChunk
from app.services.document_store import document_store
from app.services.gemma_client import GemmaAPIError, GemmaTimeoutError
from app.services.rewrite_service import rewrite_document, rewritten_chunks_to_full_text
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
        results = await rewrite_document(document, body.mode)
    except GemmaTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "gemma_timeout", "message": "Gemma API timed out during rewriting."}})
    except GemmaAPIError as exc:
        log_event(logger, "rewrite_gemma_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "gemma_api_error", "message": "Gemma API call failed."}})
    except JsonParseError as exc:
        log_event(logger, "rewrite_json_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "invalid_model_output", "message": "Model did not return valid JSON."}})

    return RewriteResponse(
        document_id=body.document_id,
        mode=body.mode,
        rewritten_text=rewritten_chunks_to_full_text(results),
        chunks=[RewrittenChunk(**r) for r in results],
    )
