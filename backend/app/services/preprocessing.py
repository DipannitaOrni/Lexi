"""
Preprocessing pipeline applied to raw extracted text before chunking.

Steps (per design doc Section 4.2), applied in order:
1. Whitespace cleaning
2. Unicode normalization
3. Page merging (implicit — extractors already join pages with \n\n)
4. Header/footer removal (repeated short lines across the document)
5. Broken line fixing
"""
import re
import unicodedata
from collections import Counter
from typing import List

_MULTI_SPACE_RE = re.compile(r"[ \t]+")
_MULTI_BLANK_LINE_RE = re.compile(r"\n{3,}")
_TERMINAL_PUNCT = (".", "!", "?", ":", ";")
_BULLET_PREFIXES = ("-", "*", "•", "–")


def clean_whitespace(text: str) -> str:
    lines = [_MULTI_SPACE_RE.sub(" ", line).strip() for line in text.split("\n")]
    joined = "\n".join(lines)
    return _MULTI_BLANK_LINE_RE.sub("\n\n", joined).strip()


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def remove_repeated_headers_footers(text: str, min_repeat_ratio: float = 0.6) -> str:
    """
    Detects short lines (likely headers/footers/page numbers) that repeat
    across a large fraction of the document's paragraph blocks, and strips
    them. Only applied to short lines (<80 chars) to avoid removing real
    content that happens to repeat (e.g., a recurring key term).
    """
    blocks = [b for b in text.split("\n\n") if b.strip()]
    if len(blocks) < 4:
        return text  # not enough blocks to detect a meaningful repeat pattern

    line_counts: Counter = Counter()
    for block in blocks:
        first_line = block.split("\n")[0].strip()
        if first_line and len(first_line) < 80:
            line_counts[first_line] += 1

    threshold = max(2, int(len(blocks) * min_repeat_ratio))
    repeated_lines = {line for line, count in line_counts.items() if count >= threshold}

    if not repeated_lines:
        return text

    cleaned_blocks = []
    for block in blocks:
        lines = block.split("\n")
        if lines and lines[0].strip() in repeated_lines:
            lines = lines[1:]
        remaining = "\n".join(lines).strip()
        if remaining:
            cleaned_blocks.append(remaining)

    return "\n\n".join(cleaned_blocks)


def fix_broken_lines(text: str) -> str:
    """
    PDFs frequently break sentences mid-line without punctuation. If a line
    doesn't end in terminal punctuation and the next line doesn't start with
    a capital letter or a bullet marker, join them with a space.
    """
    blocks = text.split("\n\n")
    fixed_blocks: List[str] = []

    for block in blocks:
        lines = block.split("\n")
        merged: List[str] = []
        buffer = ""

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if not buffer:
                buffer = stripped
                continue

            buffer_ends_terminal = buffer.endswith(_TERMINAL_PUNCT)
            next_starts_bullet_or_capital = stripped.startswith(_BULLET_PREFIXES) or (
                stripped[0].isupper() if stripped else False
            )

            if buffer_ends_terminal or next_starts_bullet_or_capital:
                merged.append(buffer)
                buffer = stripped
            else:
                buffer = f"{buffer} {stripped}"

        if buffer:
            merged.append(buffer)

        fixed_blocks.append("\n".join(merged))

    return "\n\n".join(fixed_blocks)


def preprocess(raw_text: str) -> str:
    text = clean_whitespace(raw_text)
    text = normalize_unicode(text)
    text = remove_repeated_headers_footers(text)
    text = fix_broken_lines(text)
    return text
