"""
TXT extraction with encoding fallback: try UTF-8 first, then fall back to
charset-normalizer's best-guess detection for legacy encodings.
"""
from app.services.extraction.base import ExtractedDocument

try:
    from charset_normalizer import from_bytes
except ImportError:  # pragma: no cover
    from_bytes = None


def extract_txt(file_bytes: bytes) -> ExtractedDocument:
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        if from_bytes is not None:
            best_guess = from_bytes(file_bytes).best()
            text = str(best_guess) if best_guess else file_bytes.decode("utf-8", errors="replace")
        else:
            text = file_bytes.decode("utf-8", errors="replace")

    return ExtractedDocument(raw_text=text, page_count=1, warnings=[], source_format="txt")


def extract_pasted_text(text: str) -> ExtractedDocument:
    return ExtractedDocument(raw_text=text, page_count=1, warnings=[], source_format="pasted_text")
