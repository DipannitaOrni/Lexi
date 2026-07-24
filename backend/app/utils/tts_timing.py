"""
Word-timing estimation for synced highlighting during read-aloud playback.

Our local TTS engine (Kokoro) does not return word-level timestamps, so timing is
estimated from a words-per-minute speech rate adjusted for the requested
playback speed and each word's length (longer words get proportionally
more time, matching how speech actually sounds). This is an approximation,
not exact alignment — fine for highlighting sync, which tolerates small
drift, especially over short/medium passages.
"""
import re
from typing import List

from app.schemas.audio_schema import WordTiming

_BASE_WORDS_PER_MINUTE = 150  # a natural, moderate reading pace at speed=1.0
_WORD_RE = re.compile(r"\S+")


def estimate_word_timings(text: str, speed: float = 1.0) -> List[WordTiming]:
    words = _WORD_RE.findall(text)
    if not words:
        return []

    effective_wpm = _BASE_WORDS_PER_MINUTE * max(0.5, min(2.0, speed))
    base_seconds_per_word = 60.0 / effective_wpm

    # Weight each word's duration by its character length relative to the
    # average, so "and" doesn't take as long as "responsibility".
    lengths = [max(len(w), 1) for w in words]
    avg_length = sum(lengths) / len(lengths)

    timings: List[WordTiming] = []
    cursor = 0.0
    for word, length in zip(words, lengths):
        weight = length / avg_length
        duration = base_seconds_per_word * weight
        timings.append(WordTiming(word=word, start=round(cursor, 3), end=round(cursor + duration, 3)))
        cursor += duration

    return timings
