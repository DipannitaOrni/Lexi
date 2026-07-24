"""
Chunking utilities.

Rules (per design doc Section 4.3):
- Split at paragraph boundaries first.
- Only split mid-paragraph if a single paragraph exceeds the token budget,
  in which case split at sentence boundaries.
- Never split mid-sentence.
"""
import re
import uuid
from dataclasses import dataclass, field
from typing import List

from app.utils.token_estimation import estimate_tokens

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    chunk_id: str
    text: str
    order: int
    token_estimate: int = field(default=0)

    def __post_init__(self):
        if not self.token_estimate:
            self.token_estimate = estimate_tokens(self.text)


def _split_paragraph_into_sentences(paragraph: str) -> List[str]:
    sentences = _SENTENCE_SPLIT_RE.split(paragraph.strip())
    return [s for s in sentences if s.strip()]


def chunk_text(text: str, max_tokens_per_chunk: int, doc_prefix: str = "chunk") -> List[Chunk]:
    """
    Split `text` (already preprocessed) into a list of Chunk objects, each
    under max_tokens_per_chunk estimated tokens, preferring paragraph
    boundaries and falling back to sentence boundaries only when a single
    paragraph alone exceeds the budget.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # Expand any paragraph that alone exceeds the budget into sentence-level units
    units: List[str] = []
    for para in paragraphs:
        if estimate_tokens(para) <= max_tokens_per_chunk:
            units.append(para)
        else:
            units.extend(_split_paragraph_into_sentences(para))

    chunks: List[Chunk] = []
    current_parts: List[str] = []
    current_tokens = 0
    order = 0

    def flush():
        nonlocal current_parts, current_tokens, order
        if not current_parts:
            return
        chunk_text_value = "\n\n".join(current_parts)
        chunks.append(
            Chunk(
                chunk_id=f"{doc_prefix}_{order}_{uuid.uuid4().hex[:6]}",
                text=chunk_text_value,
                order=order,
            )
        )
        order += 1
        current_parts = []
        current_tokens = 0

    for unit in units:
        unit_tokens = estimate_tokens(unit)
        if current_tokens + unit_tokens > max_tokens_per_chunk and current_parts:
            flush()
        current_parts.append(unit)
        current_tokens += unit_tokens

    flush()

    if not chunks:
        # Degenerate case: empty text
        chunks.append(Chunk(chunk_id=f"{doc_prefix}_0_{uuid.uuid4().hex[:6]}", text="", order=0))

    return chunks
