"""
Stage 3 — Contextual Question Answering.

Always answers from the ORIGINAL document text, never the rewritten
version. For short documents, the full original text is injected. For long
documents, semantic retrieval (EmbeddingGemma embeddings + cosine similarity)
selects the top-k most relevant chunks. Chunk embeddings are computed once
per document and cached in the document store. Falls back to keyword
overlap if the embeddings call fails, so Q&A still works without a hard
dependency on embeddings being reachable.
"""
import re
from typing import List, Tuple

import numpy as np

from app.config import get_settings
from app.prompts.qa_prompts import build_qa_user_prompt
from app.prompts.system_prompts import QA_SYSTEM_PROMPT
from app.services.document_store import StoredDocument, document_store
from app.services.gemma_client import LLMAPIError, call_llm, get_embedding
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


def _keyword_score(question_terms: List[str], chunk_text: str) -> int:
    chunk_term_set = set(_tokenize(chunk_text))
    return sum(1 for t in question_terms if t in chunk_term_set)


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    denom = (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)) or 1e-8
    return float(np.dot(a_arr, b_arr) / denom)


async def _ensure_chunk_embeddings(document: StoredDocument) -> bool:
    """Populates document.chunk_embeddings for any chunk missing one. Returns False if embeddings are unavailable."""
    missing = [c for c in document.chunks if c.chunk_id not in document.chunk_embeddings]
    if not missing:
        return True
    try:
        for chunk in missing:
            embedding = await get_embedding(chunk.text)
            document.chunk_embeddings[chunk.chunk_id] = embedding
        document_store.save(document)
        return True
    except LLMAPIError as exc:
        log_event(logger, "embedding_unavailable_fallback_keyword", level="warning", error=str(exc))
        return False


async def _select_context_chunks(document: StoredDocument, question: str) -> List[Tuple[str, str]]:
    settings = get_settings()
    full_text_tokens = estimate_tokens(document.preprocessed_text)

    if full_text_tokens <= settings.usable_input_tokens:
        return [(c.chunk_id, c.text) for c in document.chunks]

    embeddings_ready = await _ensure_chunk_embeddings(document)

    if embeddings_ready:
        try:
            question_embedding = await get_embedding(question)
            scored = [
                (chunk, _cosine_similarity(question_embedding, document.chunk_embeddings[chunk.chunk_id]))
                for chunk in document.chunks
            ]
            scored.sort(key=lambda pair: pair[1], reverse=True)
            top_chunks = [c for c, score in scored[:_TOP_K_CHUNKS]]
            top_chunks.sort(key=lambda c: c.order)
            return [(c.chunk_id, c.text) for c in top_chunks]
        except LLMAPIError:
            pass  # fall through to keyword retrieval below

    # Keyword-overlap fallback (also used if embeddings are unavailable)
    question_terms = _tokenize(question)
    scored = [(chunk, _keyword_score(question_terms, chunk.text)) for chunk in document.chunks]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    top_chunks = [c for c, score in scored[:_TOP_K_CHUNKS]]
    top_chunks.sort(key=lambda c: c.order)
    return [(c.chunk_id, c.text) for c in top_chunks]


async def answer_question(document: StoredDocument, question: str) -> dict:
    context_chunks = await _select_context_chunks(document, question)
    user_prompt = build_qa_user_prompt(context_chunks, question)

    raw_response = await call_llm(
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
        raw_response = await call_llm(
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
