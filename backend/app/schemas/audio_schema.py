from typing import List, Optional

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    document_id: Optional[str] = None
    text: Optional[str] = None
    mode: Optional[str] = None
    reading_level: int = 3
    voice: Optional[str] = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    session_id: Optional[str] = None  # if given, saves voice/speed as the session's preference


class WordTiming(BaseModel):
    word: str
    start: float
    end: float


class TimedTTSResponse(BaseModel):
    audio_base64: str
    duration_seconds: float
    words: List[WordTiming]


class TranscribeResponse(BaseModel):
    text: str
