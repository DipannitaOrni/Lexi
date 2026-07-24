from typing import List, Optional

from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    document_id: str
    mode: str
    reading_level: int = Field(default=3, ge=1, le=5)


class VerificationWarning(BaseModel):
    type: str
    description: str
    original_excerpt: str
    rewritten_excerpt: str
    chunk_id: Optional[str] = None


class VerifyResponse(BaseModel):
    document_id: str
    confidence_score: float
    is_safe: bool
    warnings: List[VerificationWarning] = []


class ReadabilityStatsModel(BaseModel):
    word_count: int
    sentence_count: int
    avg_words_per_sentence: float
    flesch_kincaid_grade: float


class DocumentStats(BaseModel):
    original: ReadabilityStatsModel
    rewritten: ReadabilityStatsModel


class ProcessRequest(BaseModel):
    document_id: str
    mode: str
    reading_level: int = Field(default=3, ge=1, le=5)


class ProcessResponse(BaseModel):
    document_id: str
    mode: str
    reading_level: int
    rewritten_text: str
    verification: Optional[VerifyResponse] = None
    verification_error: Optional[str] = None
    stats: Optional[DocumentStats] = None
