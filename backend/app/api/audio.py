"""
POST /transcribe — transcribes an uploaded audio clip to text (Whisper),
for the ChatBox.jsx voice-input feature.
"""
import base64
import io

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.schemas.audio_schema import TranscribeResponse
from app.services.document_store import document_store
from app.services.gemma_client import LLMAPIError, LLMTimeoutError, transcribe_audio
from app.services.rewrite_service import rewrite_document, rewritten_chunks_to_full_text
from app.services.session_store import session_store
from app.utils.logging_config import get_logger, log_event

router = APIRouter()
logger = get_logger("api.audio")

_MAX_AUDIO_FILE_MB = 25




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
