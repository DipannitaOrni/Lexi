"""
POST /export — produces a downloadable file (txt, pdf, or audio) of a
document's rewrite, so users can save and use the accessible version
offline. Powers a "Download" action in the frontend.
"""
import io
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from fpdf import FPDF

from app.schemas.export_schema import ExportRequest
from app.services.document_store import document_store
from app.services.gemma_client import LLMAPIError, LLMTimeoutError, synthesize_speech
from app.services.rewrite_service import rewrite_document, rewritten_chunks_to_full_text
from app.utils.logging_config import get_logger, log_event

router = APIRouter()
logger = get_logger("api.export")

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
BENGALI_FONT = os.path.join(FONT_DIR, "NotoSansBengali-Regular.ttf")
LATIN_FONT = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def _has_bengali(text: str) -> bool:
    return any('\u0980' <= ch <= '\u09FF' for ch in text)


def _build_pdf_bytes(title: str, text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    use_bengali = _has_bengali(text) or _has_bengali(title)

    if use_bengali and os.path.exists(BENGALI_FONT):
        pdf.add_font("NotoBengali", "", BENGALI_FONT)
        font_name = "NotoBengali"
    elif os.path.exists(LATIN_FONT):
        pdf.add_font("DejaVu", "", LATIN_FONT)
        font_name = "DejaVu"
    else:
        font_name = "Helvetica"

    pdf.set_font(font_name, size=16)
    pdf.multi_cell(0, 10, title)
    pdf.ln(4)

    pdf.set_font(font_name, size=12)
    for para in text.split("\n"):
        if para.strip():
            pdf.multi_cell(0, 8, para)
        else:
            pdf.ln(4)

    return bytes(pdf.output())


@router.post("/export")
async def export(body: ExportRequest):
    document = document_store.get(body.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    try:
        results = await rewrite_document(document, body.mode, body.reading_level)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "LLM API timed out during rewriting."}})
    except LLMAPIError as exc:
        log_event(logger, "export_rewrite_failed", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "LLM API call failed."}})

    rewritten_text = rewritten_chunks_to_full_text(results)
    filename_base = f"lexi_{body.document_id[:8]}_{body.mode}"

    if body.format == "txt":
        return StreamingResponse(
            io.BytesIO(rewritten_text.encode("utf-8")),
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.txt"'},
        )

    if body.format == "pdf":
        # Unicode-safe: embeds a TTF so non-Latin scripts (e.g. Bangla) render
        # correctly. Falls back to Helvetica only if no font files are present.
        pdf_bytes = _build_pdf_bytes(f"Lexi — {body.mode} mode", rewritten_text)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.pdf"'},
        )

    try:
        audio_bytes = await synthesize_speech(rewritten_text)
    except LLMTimeoutError:
        raise HTTPException(status_code=504, detail={"error": {"code": "llm_timeout", "message": "Speech synthesis timed out."}})
    except LLMAPIError as exc:
        log_event(logger, "export_tts_failed", level="error", error=str(exc))
        raise HTTPException(status_code=502, detail={"error": {"code": "llm_api_error", "message": "Speech synthesis failed."}})

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"Content-Disposition": f'attachment; filename="{filename_base}.mp3"'},
    )
