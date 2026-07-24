"""
POST /visualize — OPTIONAL, user-triggered: generates a flowchart (Mermaid
syntax) or chart (labels/values) summarizing the document's structure or
data, so users who want a visual overview can request one on demand.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.visualize_schema import VisualizeRequest, VisualizeResponse
from app.services.document_store import document_store
from app.services.gemma_client import LLMAPIError, LLMTimeoutError
from app.services.visualize_service import generate_visualization
from app.utils.json_parsing import JsonParseError
from app.utils.logging_config import get_logger, log_event

router = APIRouter()
logger = get_logger("api.visualize")


@router.post("/visualize", response_model=VisualizeResponse)
async def visualize(body: VisualizeRequest):
    document = document_store.get(body.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    try:
        result = await generate_visualization(document)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "LLM API timed out generating visualization."}})
    except LLMAPIError as exc:
        log_event(logger, "visualize_llm_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "LLM API call failed."}})

    return VisualizeResponse(document_id=body.document_id, **result)
