"""
Common interface + result type for all format-specific extractors, so the
rest of the pipeline never has to know which format the document came from.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class PageWarning:
    page_number: int
    reason: str  # e.g. "scanned_no_ocr", "garbled_text"


@dataclass
class ExtractedDocument:
    raw_text: str
    page_count: int
    warnings: List[PageWarning] = field(default_factory=list)
    source_format: str = ""
