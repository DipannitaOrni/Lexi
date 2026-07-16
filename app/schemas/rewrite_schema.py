from typing import List, Literal, Optional

from pydantic import BaseModel, Field

AccessibilityMode = Literal["dyslexia", "focus", "screen_reader", "non_native"]


class RewriteRequest(BaseModel):
    document_id: str
    mode: AccessibilityMode


class RewrittenChunk(BaseModel):
    chunk_id: str
    rewritten_text: str
    mode: str


class RewriteResponse(BaseModel):
    document_id: str
    mode: str
    rewritten_text: str
    chunks: List[RewrittenChunk]
