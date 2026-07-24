from typing import Literal, Optional

from pydantic import BaseModel, Field


class PreferencesUpdateRequest(BaseModel):
    session_id: str
    voice: Optional[str] = None
    speed: Optional[float] = Field(default=None, ge=0.5, le=2.0)


class PreferencesResponse(BaseModel):
    session_id: str
    voice: str
    speed: float


class ProgressUpdateRequest(BaseModel):
    session_id: str
    document_id: str
    chunk_id: str
    status: Literal["read", "listened"]


class ProgressResponse(BaseModel):
    document_id: str
    total_chunks: int
    completed_chunk_ids: list
    percent_complete: float
