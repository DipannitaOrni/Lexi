"""
Structured JSON-line logging so a full pipeline run can be reconstructed
from logs alone during debugging or judging Q&A.

Never logs: raw API keys, full document content. Only excerpts/lengths.
"""
import json
import logging
import sys
import time
from typing import Any, Dict, Optional


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": round(time.time(), 3),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if extra:
            payload.update(extra)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers on reload
    root.handlers = []
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(logger: logging.Logger, message: str, level: str = "info", **fields: Any) -> None:
    """Convenience helper: log_event(logger, "gemma_call_end", latency_ms=123, stage="rewrite")"""
    log_fn = getattr(logger, level, logger.info)
    log_fn(message, extra={"extra_fields": fields})


def safe_excerpt(text: Optional[str], max_len: int = 120) -> str:
    """Never log full document content — only a bounded excerpt."""
    if not text:
        return ""
    text = text.replace("\n", " ")
    return text[:max_len] + ("..." if len(text) > max_len else "")
