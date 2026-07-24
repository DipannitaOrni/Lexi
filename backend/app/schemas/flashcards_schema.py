from typing import List

from pydantic import BaseModel


class FlashcardsRequest(BaseModel):
    document_id: str
    max_total: int = 15


class Flashcard(BaseModel):
    question: str
    answer: str
    chunk_id: str


class FlashcardsResponse(BaseModel):
    document_id: str
    flashcards: List[Flashcard]
