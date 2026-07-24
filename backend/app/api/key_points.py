"""
POST /key-points — mode-independent short summary from the ORIGINAL
document, for the KeyPoints.jsx frontend component.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.key_points_schema import KeyPointsRequest, KeyPointsResponse
from app.services.document_store import document_store
from app.services.key_points_service import extract_key_points
from app.services.gemma_client import LLMAPIError, LLMTimeoutError
from app.utils.logging_config import get_logger, log_event

router = APIRouter()
logger = get_logger("api.key_points")


@router.post("/key-points", response_model=KeyPointsResponse)
async def key_points(body: KeyPointsRequest):
    document = document_store.get(body.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    try:
        points = await extract_key_points(document)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "LLM API timed out extracting key points."}})
    except LLMAPIError as exc:
        log_event(logger, "key_points_llm_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "LLM API call failed."}})

    return KeyPointsResponse(document_id=body.document_id, key_points=points)
