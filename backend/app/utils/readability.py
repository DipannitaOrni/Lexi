"""
Pure-Python readability scoring — no extra dependency needed.

Computes a Flesch-Kincaid-style grade level plus basic counts, used to show
the "before vs after" reading-level stat card (StatsRow.jsx). This is an
approximation (English-tuned heuristic); it is informational for the UI,
not a factual claim verified by Stage 2.
"""
import re
from dataclasses import dataclass

_WORD_RE = re.compile(r"[A-Za-z]+")
_SENTENCE_SPLIT_RE = re.compile(r"[.!?]+")
_VOWEL_GROUPS_RE = re.compile(r"[aeiouyAEIOUY]+")


@dataclass
class ReadabilityStats:
    word_count: int
    sentence_count: int
    avg_words_per_sentence: float
    flesch_kincaid_grade: float


def _count_syllables(word: str) -> int:
    word = word.lower()
    groups = _VOWEL_GROUPS_RE.findall(word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def compute_readability(text: str) -> ReadabilityStats:
    words = _WORD_RE.findall(text)
    sentences = [s for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]

    word_count = len(words)
    sentence_count = max(len(sentences), 1)

    if word_count == 0:
        return ReadabilityStats(0, 0, 0.0, 0.0)

    syllable_count = sum(_count_syllables(w) for w in words)
    avg_words_per_sentence = word_count / sentence_count
    avg_syllables_per_word = syllable_count / word_count

    # Flesch-Kincaid Grade Level formula
    grade = 0.39 * avg_words_per_sentence + 11.8 * avg_syllables_per_word - 15.59
    grade = max(0.0, round(grade, 1))

    return ReadabilityStats(
        word_count=word_count,
        sentence_count=sentence_count,
        avg_words_per_sentence=round(avg_words_per_sentence, 1),
        flesch_kincaid_grade=grade,
    )
