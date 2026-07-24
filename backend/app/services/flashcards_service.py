"""
Flashcard generation — an additional stage that produces short, strictly
grounded Q/A study cards from the ORIGINAL document, powering the
Flashcards.jsx frontend component.
"""
import asyncio
from typing import List

from app.prompts.flashcards_prompts import build_flashcards_user_prompt
from app.prompts.system_prompts import FLASHCARDS_SYSTEM_PROMPT
from app.services.document_store import StoredDocument
from app.services.gemma_client import call_llm
from app.utils.json_parsing import JsonParseError, parse_json_safely
from app.utils.logging_config import get_logger, log_event

logger = get_logger("flashcards_service")

_MAX_CONCURRENT_CALLS = 4
_MAX_CARDS_PER_CHUNK = 5


async def _flashcards_for_chunk(chunk_text: str, chunk_id: str, semaphore: asyncio.Semaphore) -> List[dict]:
    user_prompt = build_flashcards_user_prompt(chunk_text, chunk_id, _MAX_CARDS_PER_CHUNK)
    async with semaphore:
        raw_response = await call_llm(
            system_prompt=FLASHCARDS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
            stage="flashcards",
        )
    try:
        parsed = parse_json_safely(raw_response)
    except JsonParseError:
        log_event(logger, "flashcards_json_parse_failed", level="warning", chunk_id=chunk_id)
        return []
    return parsed.get("flashcards", [])


async def generate_flashcards(document: StoredDocument, max_total: int = 15) -> List[dict]:
    semaphore = asyncio.Semaphore(_MAX_CONCURRENT_CALLS)
    tasks = [_flashcards_for_chunk(c.text, c.chunk_id, semaphore) for c in document.chunks]
    results = await asyncio.gather(*tasks)
    all_cards = [card for chunk_cards in results for card in chunk_cards]
    return all_cards[:max_total]
