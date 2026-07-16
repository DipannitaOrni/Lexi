"""
Stage 3 — Contextual Question Answering.

Always answers from the ORIGINAL document text, never the rewritten
version (see design doc Section 7.1). For short documents, the full
original text is injected. For long documents, a lightweight keyword-
overlap retrieval step selects the top-k most relevant chunks, avoiding
an embedding-model dependency under hackathon time pressure.
"""
import re
from typing import List, Tuple

from app.config import get_settings
from app.prompts.qa_prompts import build_qa_user_prompt
from app.prompts.system_prompts import QA_SYSTEM_PROMPT
from app.services.document_store import StoredDocument
from app.services.gemma_client import call_gemma
from app.utils.json_parsing import JsonParseError, parse_json_safely
from app.utils.logging_config import get_logger, log_event
from app.utils.token_estimation import estimate_tokens

logger = get_logger("qa_service")

_TOP_K_CHUNKS = 5
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "in", "on", "for",
    "and", "or", "what", "when", "where", "who", "how", "does", "do", "did",
    "this", "that", "with", "it", "as", "be", "by", "at", "from",
}


def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS]


def _score_chunk(question_terms: List[str], chunk_text: str) -> int:
    chunk_terms = _tokenize(chunk_text)
    chunk_term_set = set(chunk_terms)
    return sum(1 for t in question_terms if t in chunk_term_set)


def _select_context_chunks(document: StoredDocument, question: str) -> List[Tuple[str, str]]:
    settings = get_settings()
    full_text_tokens = estimate_tokens(document.preprocessed_text)

    if full_text_tokens <= settings.usable_input_tokens:
        # Short document: inject everything, one "chunk" per stored chunk so
        # citations still resolve to a chunk_id.
        return [(c.chunk_id, c.text) for c in document.chunks]

    # Long document: keyword-overlap retrieval over stored chunks.
    question_terms = _tokenize(question)
    scored = [
        (chunk, _score_chunk(question_terms, chunk.text))
        for chunk in document.chunks
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    top_chunks = [c for c, score in scored[:_TOP_K_CHUNKS]]
    # Preserve original document order among the selected chunks for readability
    top_chunks.sort(key=lambda c: c.order)
    return [(c.chunk_id, c.text) for c in top_chunks]


async def answer_question(document: StoredDocument, question: str) -> dict:
    context_chunks = _select_context_chunks(document, question)
    user_prompt = build_qa_user_prompt(context_chunks, question)

    raw_response = await call_gemma(
        system_prompt=QA_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.1,
        stage="qa",
    )

    try:
        parsed = parse_json_safely(raw_response)
    except JsonParseError:
        log_event(logger, "qa_json_parse_retry", level="warning", document_id=document.document_id)
        corrected_prompt = user_prompt + "\n\nReminder: return ONLY valid JSON, nothing else."
        raw_response = await call_gemma(
            system_prompt=QA_SYSTEM_PROMPT,
            user_prompt=corrected_prompt,
            temperature=0.0,
            stage="qa_retry",
        )
        parsed = parse_json_safely(raw_response)

    parsed.setdefault("answer", None)
    parsed.setdefault("supporting_excerpt", None)
    parsed.setdefault("source_chunk_id", None)
    parsed.setdefault("found_in_document", parsed.get("answer") is not None)

    log_event(
        logger, "qa_complete", document_id=document.document_id,
        found_in_document=parsed["found_in_document"], chunks_used=len(context_chunks),
    )
    return parsed
