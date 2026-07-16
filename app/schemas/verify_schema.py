from typing import List, Optional

from pydantic import BaseModel


class VerifyRequest(BaseModel):
    document_id: str
    rewritten_text: Optional[str] = None  # if omitted, verifies the cached rewrite for `mode`
    mode: Optional[str] = None


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


class ProcessRequest(BaseModel):
    document_id: str
    mode: str


class ProcessResponse(BaseModel):
    document_id: str
    mode: str
    rewritten_text: str
    verification: Optional[VerifyResponse] = None
    verification_error: Optional[str] = None
