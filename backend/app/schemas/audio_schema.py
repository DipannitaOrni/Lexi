from typing import List, Optional

from pydantic import BaseModel, Field

class WordTiming(BaseModel):
    word: str
    start: float
    end: float

class TranscribeResponse(BaseModel):
    text: str

class TtsTimedRequest(BaseModel):
    text: str
    document_id: Optional[str] = None
    mode: Optional[str] = None
    reading_level: int = 3
    voice: Optional[str] = None
    speed: float = 1.0

class TtsTimedResponse(BaseModel):
    audio_base64: str
    words: List[WordTiming]
