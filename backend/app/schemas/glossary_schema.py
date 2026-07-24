from typing import List

from pydantic import BaseModel


class GlossaryRequest(BaseModel):
    document_id: str
    max_terms: int = 20


class GlossaryTerm(BaseModel):
    term: str
    definition: str
    chunk_id: str


class GlossaryResponse(BaseModel):
    document_id: str
    terms: List[GlossaryTerm]
