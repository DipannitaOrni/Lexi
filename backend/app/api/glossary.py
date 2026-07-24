"""
POST /glossary — detects jargon/technical terms in the document and
returns short, document-grounded definitions for tap-to-define.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.glossary_schema import GlossaryRequest, GlossaryResponse, GlossaryTerm
from app.services.document_store import document_store
from app.services.glossary_service import extract_glossary
from app.services.gemma_client import LLMAPIError, LLMTimeoutError
from app.utils.logging_config import get_logger, log_event

router = APIRouter()
logger = get_logger("api.glossary")


@router.post("/glossary", response_model=GlossaryResponse)
async def glossary(body: GlossaryRequest):
    document = document_store.get(body.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    try:
        terms = await extract_glossary(document, body.max_terms)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "LLM API timed out extracting glossary terms."}})
    except LLMAPIError as exc:
        log_event(logger, "glossary_llm_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "LLM API call failed."}})

    return GlossaryResponse(document_id=body.document_id, terms=[GlossaryTerm(**t) for t in terms])
