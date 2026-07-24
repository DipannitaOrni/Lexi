"""
POST /tts — synthesizes speech audio from either raw text or a document's
cached rewrite, for AudioControls.jsx.

POST /tts/timed — same, but also returns estimated word-level timings for
synced word-by-word highlighting during playback (returns audio as base64
JSON so the timing array can travel alongside it in one response).

POST /transcribe — transcribes an uploaded audio clip to text (Whisper),
for the ChatBox.jsx voice-input feature.
"""
import base64
import io

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.schemas.audio_schema import TimedTTSResponse, TranscribeResponse, TTSRequest
from app.services.document_store import document_store
from app.services.gemma_client import LLMAPIError, LLMTimeoutError, text_to_speech, transcribe_audio
from app.services.rewrite_service import rewrite_document, rewritten_chunks_to_full_text
from app.services.session_store import session_store
from app.utils.logging_config import get_logger, log_event
from app.utils.tts_timing import estimate_word_timings

router = APIRouter()
logger = get_logger("api.audio")

_MAX_AUDIO_FILE_MB = 25


async def _resolve_text_and_voice(body: TTSRequest) -> tuple[str, str, float]:
    if not body.document_id and not body.text:
        raise HTTPException(status_code=400, detail={"error": {"code": "no_text_source", "message": "Provide either document_id or text."}})

    text_to_read = body.text
    if not text_to_read and body.document_id:
        document = document_store.get(body.document_id)
        if document is None:
            raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})
        try:
            results = await rewrite_document(document, body.mode or "screen_reader", body.reading_level)
        except (LLMAPIError, LLMTimeoutError) as exc:
            log_event(logger, "tts_rewrite_failed", level="error", error=str(exc))
            raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "Could not prepare text for speech."}})
        text_to_read = rewritten_chunks_to_full_text(results)

    if not text_to_read.strip():
        raise HTTPException(status_code=422, detail={"error": {"code": "empty_text", "message": "Nothing to synthesize."}})

    voice, speed = body.voice, body.speed
    if body.session_id:
        # Session preference is the default; explicit request fields override it if provided.
        saved_voice, saved_speed = session_store.get_preferences(body.session_id)
        voice = body.voice or saved_voice
        speed = body.speed if body.speed != 1.0 else saved_speed
        session_store.set_preferences(body.session_id, voice, speed)

    return text_to_read, voice or "alloy", speed


@router.post("/tts")
async def tts(body: TTSRequest):
    text_to_read, voice, speed = await _resolve_text_and_voice(body)

    try:
        audio_bytes = await text_to_speech(text_to_read, voice=voice, speed=speed)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "TTS request timed out."}})
    except LLMAPIError as exc:
        log_event(logger, "tts_llm_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "TTS request failed."}})

    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")


@router.post("/tts/timed", response_model=TimedTTSResponse)
async def tts_timed(body: TTSRequest):
    text_to_read, voice, speed = await _resolve_text_and_voice(body)

    try:
        audio_bytes = await text_to_speech(text_to_read, voice=voice, speed=speed)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "TTS request timed out."}})
    except LLMAPIError as exc:
        log_event(logger, "tts_llm_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "TTS request failed."}})

    words = estimate_word_timings(text_to_read, speed=speed)
    duration = words[-1].end if words else 0.0

    return TimedTTSResponse(
        audio_base64=base64.b64encode(audio_bytes).decode("ascii"),
        duration_seconds=duration,
        words=words,
    )


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)):
    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > _MAX_AUDIO_FILE_MB:
        raise HTTPException(status_code=413, detail={"error": {"code": "file_too_large", "message": f"Audio is {size_mb:.1f}MB, max is {_MAX_AUDIO_FILE_MB}MB."}})
    if not file_bytes:
        raise HTTPException(status_code=422, detail={"error": {"code": "empty_file", "message": "Uploaded audio is empty."}})

    try:
        text = await transcribe_audio(file_bytes, file.filename or "audio.webm")
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "Transcription timed out."}})
    except LLMAPIError as exc:
        log_event(logger, "transcribe_llm_error", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "Transcription failed."}})

    return TranscribeResponse(text=text)
