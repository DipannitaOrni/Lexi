"""
Key-points extraction — mode-independent short summary from the ORIGINAL
document, powering the KeyPoints.jsx frontend component.
"""
from app.prompts.key_points_prompts import build_key_points_user_prompt
from app.prompts.system_prompts import KEY_POINTS_SYSTEM_PROMPT
from app.services.document_store import StoredDocument
from app.services.gemma_client import call_llm
from app.utils.json_parsing import JsonParseError, parse_json_safely
from app.utils.logging_config import get_logger, log_event

logger = get_logger("key_points_service")


async def extract_key_points(document: StoredDocument) -> list:
    # Use only the first ~2 chunks worth of text for a fast, cheap summary —
    # key points are meant to be a quick orientation, not exhaustive.
    text = "\n\n".join(c.text for c in document.chunks[:2])
    user_prompt = build_key_points_user_prompt(text)

    raw_response = await call_llm(
        system_prompt=KEY_POINTS_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2,
        stage="key_points",
    )
    try:
        parsed = parse_json_safely(raw_response)
    except JsonParseError:
        log_event(logger, "key_points_json_parse_failed", level="warning", document_id=document.document_id)
        return []
    return parsed.get("key_points", [])
