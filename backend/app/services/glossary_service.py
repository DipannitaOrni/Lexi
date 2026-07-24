"""
Glossary/term-explainer — detects jargon in the ORIGINAL document and
produces short, document-grounded definitions, powering a tap-to-define
UI feature.
"""
import asyncio
from typing import List

from app.prompts.glossary_prompts import GLOSSARY_SYSTEM_PROMPT, build_glossary_user_prompt
from app.services.document_store import StoredDocument
from app.services.gemma_client import call_llm
from app.utils.json_parsing import JsonParseError, parse_json_safely
from app.utils.logging_config import get_logger, log_event

logger = get_logger("glossary_service")

_MAX_CONCURRENT_CALLS = 4
_MAX_TERMS_PER_CHUNK = 8


async def _glossary_for_chunk(chunk_text: str, chunk_id: str, semaphore: asyncio.Semaphore) -> List[dict]:
    user_prompt = build_glossary_user_prompt(chunk_text, chunk_id, _MAX_TERMS_PER_CHUNK)
    async with semaphore:
        raw_response = await call_llm(
            system_prompt=GLOSSARY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
            stage="glossary",
        )
    try:
        parsed = parse_json_safely(raw_response)
    except JsonParseError:
        log_event(logger, "glossary_json_parse_failed", level="warning", chunk_id=chunk_id)
        return []
    return parsed.get("terms", [])


async def extract_glossary(document: StoredDocument, max_terms: int = 20) -> List[dict]:
    semaphore = asyncio.Semaphore(_MAX_CONCURRENT_CALLS)
    tasks = [_glossary_for_chunk(c.text, c.chunk_id, semaphore) for c in document.chunks]
    results = await asyncio.gather(*tasks)
    all_terms = [term for chunk_terms in results for term in chunk_terms]

    # De-duplicate by term text (case-insensitive), keeping the first definition seen
    seen = set()
    deduped = []
    for t in all_terms:
        key = t.get("term", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            deduped.append(t)

    return deduped[:max_terms]
