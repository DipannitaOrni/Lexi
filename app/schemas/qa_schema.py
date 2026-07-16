from typing import Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    document_id: str
    question: str = Field(..., min_length=1)


class AskResponse(BaseModel):
    document_id: str
    answer: Optional[str] = None
    supporting_excerpt: Optional[str] = None
    source_chunk_id: Optional[str] = None
    found_in_document: bool
