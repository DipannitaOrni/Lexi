from typing import List, Literal, Optional

from pydantic import BaseModel, Field

AccessibilityMode = Literal[
    "dyslexia", "focus", "screen_reader", "non_native", "civic", "dyscalculia", "adhd"
]


class RewriteRequest(BaseModel):
    document_id: str
    mode: AccessibilityMode
    reading_level: int = Field(default=3, ge=1, le=5, description="1=simplest, 5=closest to original complexity")


class RewrittenChunk(BaseModel):
    chunk_id: str
    rewritten_text: str
    mode: str


class RewriteResponse(BaseModel):
    document_id: str
    mode: str
    reading_level: int
    rewritten_text: str
    chunks: List[RewrittenChunk]
