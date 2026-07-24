from typing import List, Optional

from pydantic import BaseModel, Field

class WordTiming(BaseModel):
    word: str
    start: float
    end: float

class TranscribeResponse(BaseModel):
    text: str
