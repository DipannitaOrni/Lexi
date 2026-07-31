"""
POST /tts/timed — synthesizes speech for the given text and returns it
alongside estimated per-word timings, for ResultView.jsx's read-aloud
playback with synced word highlighting.
"""
import base64

from fastapi import APIRouter, HTTPException

from app.schemas.audio_schema import TtsTimedRequest, TtsTimedResponse
from app.services.gemma_client import LLMAPIError, LLMTimeoutError, synthesize_speech
from app.utils.logging_config import get_logger, log_event
from app.utils.tts_timing import estimate_word_timings

router = APIRouter()
logger = get_logger("api.tts")


@router.post("/tts/timed", response_model=TtsTimedResponse)
async def tts_timed(body: TtsTimedRequest):
    if not body.text.strip():
        raise HTTPException(status_code=422, detail={"error": {"code": "empty_text", "message": "No text to speak."}})

    try:
        audio_bytes = await synthesize_speech(body.text, voice=body.voice, speed=body.speed)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "Speech synthesis timed out."}})
    except LLMAPIError as exc:
        log_event(logger, "tts_llm_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "Speech synthesis failed."}})

    words = estimate_word_timings(body.text, speed=body.speed)

    return TtsTimedResponse(
        audio_base64=base64.b64encode(audio_bytes).decode("ascii"),
        words=words,
    )
