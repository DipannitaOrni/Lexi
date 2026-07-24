"""
POST /verify — runs Stage 2 only, against the cached Stage 1 output for a
given mode + reading level (rewrites first if not already cached).
"""
from fastapi import APIRouter, HTTPException

from app.schemas.verify_schema import VerificationWarning, VerifyRequest, VerifyResponse
from app.services.document_store import document_store
from app.services.gemma_client import LLMAPIError, LLMTimeoutError
from app.services.rewrite_service import rewrite_document
from app.services.verify_service import verify_document
from app.utils.json_parsing import JsonParseError
from app.utils.logging_config import get_logger, log_event

router = APIRouter()
logger = get_logger("api.verify")


@router.post("/verify", response_model=VerifyResponse)
async def verify(body: VerifyRequest):
    document = document_store.get(body.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    try:
        rewritten_results = await rewrite_document(document, body.mode, body.reading_level)
        cache_key = f"{body.mode}:{body.reading_level}"
        result = await verify_document(document, rewritten_results, cache_key)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "LLM API timed out during verification."}})
    except LLMAPIError as exc:
        log_event(logger, "verify_llm_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "LLM API call failed."}})
    except JsonParseError as exc:
        log_event(logger, "verify_json_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "invalid_model_output", "message": "Model did not return valid JSON."}})

    return VerifyResponse(
        document_id=body.document_id,
        confidence_score=result["confidence_score"],
        is_safe=result["is_safe"],
        warnings=[VerificationWarning(**w) for w in result["warnings"]],
    )
