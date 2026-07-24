from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class PasteTextRequest(BaseModel):
    pasted_text: str = Field(..., min_length=1)


class UploadWarning(BaseModel):
    page_number: int
    reason: str


class UploadResponse(BaseModel):
    document_id: str
    extracted_text_preview: str
    pages: int
    chunk_count: int
    warnings: List[UploadWarning] = []
