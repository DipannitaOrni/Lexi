"""
POST /flashcards — generates strictly grounded study flashcards from the
ORIGINAL document, for the Flashcards.jsx frontend component.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.flashcards_schema import Flashcard, FlashcardsRequest, FlashcardsResponse
from app.services.document_store import document_store
from app.services.flashcards_service import generate_flashcards
from app.services.gemma_client import LLMAPIError, LLMTimeoutError
from app.utils.logging_config import get_logger, log_event

router = APIRouter()
logger = get_logger("api.flashcards")


@router.post("/flashcards", response_model=FlashcardsResponse)
async def flashcards(body: FlashcardsRequest):
    document = document_store.get(body.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    try:
        cards = await generate_flashcards(document, body.max_total)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "LLM API timed out generating flashcards."}})
    except LLMAPIError as exc:
        log_event(logger, "flashcards_llm_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "LLM API call failed."}})

    return FlashcardsResponse(document_id=body.document_id, flashcards=[Flashcard(**c) for c in cards])
