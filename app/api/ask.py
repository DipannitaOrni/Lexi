"""
POST /ask — runs Stage 3, grounded strictly in the ORIGINAL document text.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.qa_schema import AskRequest, AskResponse
from app.services.document_store import document_store
from app.services.gemma_client import GemmaAPIError, GemmaTimeoutError
from app.services.qa_service import answer_question
from app.utils.json_parsing import JsonParseError
from app.utils.logging_config import get_logger, log_event

router = APIRouter()
logger = get_logger("api.ask")


@router.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest):
    document = document_store.get(body.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    if not body.question.strip():
        raise HTTPException(status_code=400, detail={"error": {"code": "empty_question", "message": "question must not be empty."}})

    try:
        result = await answer_question(document, body.question)
    except GemmaTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "gemma_timeout", "message": "Gemma API timed out while answering."}})
    except GemmaAPIError as exc:
        log_event(logger, "ask_gemma_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "gemma_api_error", "message": "Gemma API call failed."}})
    except JsonParseError as exc:
        log_event(logger, "ask_json_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "invalid_model_output", "message": "Model did not return valid JSON."}})

    return AskResponse(document_id=body.document_id, **result)
