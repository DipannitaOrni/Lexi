"""
PDF extraction.

Primary extractor: PyMuPDF (fitz) — fast, reliable text + layout extraction,
and lets us detect image-heavy pages that are likely scans.

Secondary/fallback: pdfplumber — used per-page when PyMuPDF's output for
that page looks garbled or unusually sparse relative to the page's visible
content (better at column/table layouts in some documents).

Scanned pages (little/no extractable text, but image content present) are
explicitly flagged rather than silently dropped or faked — there is no OCR
step here yet.
"""
import io
import re
from typing import Optional

from app.services.extraction.base import ExtractedDocument, PageWarning

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    fitz = None

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None


_GARBLED_RATIO_THRESHOLD = 0.15  # fraction of non-printable/replacement chars
_MIN_TEXT_CHARS_FOR_NON_SCAN = 20  # below this + large images => candidate scan


def _looks_garbled(text: str) -> bool:
    if not text:
        return False
    bad_chars = sum(1 for c in text if c == "\ufffd" or (ord(c) < 32 and c not in "\n\t"))
    return (bad_chars / max(len(text), 1)) > _GARBLED_RATIO_THRESHOLD


def _extract_with_pdfplumber_page(pdf_bytes: bytes, page_index: int) -> Optional[str]:
    if pdfplumber is None:
        return None
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if page_index >= len(pdf.pages):
                return None
            return pdf.pages[page_index].extract_text() or ""
    except Exception:
        return None


def extract_pdf(file_bytes: bytes) -> ExtractedDocument:
    if fitz is None:
        raise RuntimeError("PyMuPDF (fitz) is not installed")

    warnings = []
    page_texts = []

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            text = page.get_text("text") or ""

            # Detect candidate scanned pages: little/no text but significant image area
            image_list = page.get_images(full=True)
            is_sparse_text = len(text.strip()) < _MIN_TEXT_CHARS_FOR_NON_SCAN
            has_images = len(image_list) > 0

            if is_sparse_text and has_images:
                warnings.append(PageWarning(page_number=page_index + 1, reason="scanned_no_ocr"))
                text = ""  # never fabricate content for an unreadable page

            elif _looks_garbled(text):
                fallback = _extract_with_pdfplumber_page(file_bytes, page_index)
                if fallback and not _looks_garbled(fallback):
                    text = fallback
                else:
                    warnings.append(PageWarning(page_number=page_index + 1, reason="garbled_text"))

            page_texts.append(text)

        raw_text = "\n\n".join(page_texts)
        return ExtractedDocument(
            raw_text=raw_text,
            page_count=len(doc),
            warnings=warnings,
            source_format="pdf",
        )
    finally:
        doc.close()
