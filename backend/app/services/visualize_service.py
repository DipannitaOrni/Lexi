"""
Visualization generation — an OPTIONAL, user-triggered stage that decides
whether a document is better understood as a flowchart or a chart, and
produces the corresponding grounded output. Never invoked automatically.
"""
from app.prompts.visualize_prompts import VISUALIZE_SYSTEM_PROMPT, build_visualize_user_prompt
from app.services.document_store import StoredDocument
from app.services.gemma_client import call_llm
from app.utils.json_parsing import JsonParseError, parse_json_safely
from app.utils.logging_config import get_logger, log_event
from app.utils.token_estimation import estimate_tokens

logger = get_logger("visualize_service")

# Cap how much of the document we send — a visualization is meant to show
# overall structure, not encode the entire document; keeps latency/cost low.
_MAX_INPUT_CHARS = 6000


async def generate_visualization(document: StoredDocument) -> dict:
    text = document.preprocessed_text[:_MAX_INPUT_CHARS]
    user_prompt = build_visualize_user_prompt(text)

    raw_response = await call_llm(
        system_prompt=VISUALIZE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.1,
        stage="visualize",
    )

    try:
        parsed = parse_json_safely(raw_response)
    except JsonParseError:
        log_event(logger, "visualize_json_parse_failed", level="warning", document_id=document.document_id)
        return {
            "visualization_type": "none",
            "title": "",
            "mermaid_code": None,
            "chart_data": None,
            "explanation": "Could not generate a visualization for this document.",
        }

    parsed.setdefault("visualization_type", "none")
    parsed.setdefault("title", "")
    parsed.setdefault("mermaid_code", None)
    parsed.setdefault("chart_data", None)
    parsed.setdefault("explanation", "")
    return parsed
