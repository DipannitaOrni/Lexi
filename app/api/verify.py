"""
POST /verify — runs Stage 2 only. Verifies either a provided rewritten_text
against the document's original chunks (if the split aligns), or, more
commonly, verifies the cached Stage 1 output for a given mode.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.verify_schema import VerificationWarning, VerifyRequest, VerifyResponse
from app.services.document_store import document_store
from app.services.gemma_client import GemmaAPIError, GemmaTimeoutError
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

    if not body.mode:
        raise HTTPException(status_code=422, detail={"error": {"code": "mode_required", "message": "mode is required to locate the rewrite to verify."}})

    try:
        # Ensure a rewrite exists for this mode (uses cache if already rewritten)
        rewritten_results = await rewrite_document(document, body.mode)
        result = await verify_document(document, rewritten_results, body.mode)
    except GemmaTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "gemma_timeout", "message": "Gemma API timed out during verification."}})
    except GemmaAPIError as exc:
        log_event(logger, "verify_gemma_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "gemma_api_error", "message": "Gemma API call failed."}})
    except JsonParseError as exc:
        log_event(logger, "verify_json_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "invalid_model_output", "message": "Model did not return valid JSON."}})

    return VerifyResponse(
        document_id=body.document_id,
        confidence_score=result["confidence_score"],
        is_safe=result["is_safe"],
        warnings=[VerificationWarning(**w) for w in result["warnings"]],
    )
