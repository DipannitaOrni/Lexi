"""
Safe parsing of JSON that an LLM was instructed to emit.
Models sometimes wrap JSON in markdown fences or add stray text —
this strips common wrappers before attempting json.loads.
"""
import json
import re
from typing import Any, Dict, Optional

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


class JsonParseError(Exception):
    pass


def parse_json_safely(raw_text: str) -> Dict[str, Any]:
    if raw_text is None:
        raise JsonParseError("Empty response from model")

    cleaned = _FENCE_RE.sub("", raw_text).strip()

    # If there's leading/trailing prose around the JSON object, extract the
    # outermost {...} span as a best-effort fallback.
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise JsonParseError(f"Could not parse model JSON output: {exc}") from exc

    raise JsonParseError("No JSON object found in model output")
