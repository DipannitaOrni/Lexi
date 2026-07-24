"""
POST /upload — accepts a PDF/DOCX/TXT file (multipart) or pasted text (JSON),
extracts and preprocesses the text, chunks it, and stores it under a new
document_id.
"""
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.schemas.upload_schema import PasteTextRequest, UploadResponse, UploadWarning
from app.services.document_store import document_store
from app.services.extraction.docx_extractor import extract_docx
from app.services.extraction.pdf_extractor import extract_pdf
from app.services.extraction.txt_extractor import extract_pasted_text, extract_txt
from app.services.preprocessing import preprocess
from app.utils.chunking import chunk_text
from app.utils.logging_config import get_logger, log_event

router = APIRouter()
logger = get_logger("api.upload")

_SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt"}


def _error(code: str, message: str, status_code: int):
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message}})


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(None)):
    settings = get_settings()

    if file is None:
        raise HTTPException(status_code=400, detail={"error": {"code": "no_file", "message": "No file provided. Use /upload/text for pasted text."}})

    extension = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
    if extension not in _SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "unsupported_format", "message": f"Unsupported format '.{extension}'. Supported: pdf, docx, txt."}},
        )

    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=413,
            detail={"error": {"code": "file_too_large", "message": f"File is {size_mb:.1f}MB, max is {settings.max_file_size_mb}MB."}},
        )
    if not file_bytes:
        raise HTTPException(status_code=422, detail={"error": {"code": "empty_file", "message": "Uploaded file is empty."}})

    try:
        if extension == "pdf":
            extracted = extract_pdf(file_bytes)
        elif extension == "docx":
            extracted = extract_docx(file_bytes)
        else:
            extracted = extract_txt(file_bytes)
    except Exception as exc:
        log_event(logger, "extraction_failed", level="error", extension=extension, error=str(exc))
        raise HTTPException(status_code=422, detail={"error": {"code": "corrupted_file", "message": f"Could not extract text: {exc}"}})

    if not extracted.raw_text.strip():
        raise HTTPException(status_code=422, detail={"error": {"code": "no_extractable_text", "message": "No text could be extracted from this file."}})

    cleaned = preprocess(extracted.raw_text)
    chunks = chunk_text(cleaned, max_tokens_per_chunk=settings.usable_input_tokens)

    stored = document_store.create(
        raw_text=extracted.raw_text,
        preprocessed_text=cleaned,
        chunks=chunks,
        extraction_warnings=extracted.warnings,
        source_format=extracted.source_format,
    )

    log_event(
        logger, "upload_complete", document_id=stored.document_id,
        source_format=extracted.source_format, chunk_count=len(chunks), pages=extracted.page_count,
    )

    return UploadResponse(
        document_id=stored.document_id,
        extracted_text_preview=cleaned[:500],
        pages=extracted.page_count,
        chunk_count=len(chunks),
        warnings=[UploadWarning(page_number=w.page_number, reason=w.reason) for w in extracted.warnings],
    )


@router.post("/upload/text", response_model=UploadResponse)
async def upload_pasted_text(body: PasteTextRequest):
    settings = get_settings()
    extracted = extract_pasted_text(body.pasted_text)

    if not extracted.raw_text.strip():
        raise HTTPException(status_code=422, detail={"error": {"code": "empty_text", "message": "Pasted text is empty."}})

    cleaned = preprocess(extracted.raw_text)
    chunks = chunk_text(cleaned, max_tokens_per_chunk=settings.usable_input_tokens)

    stored = document_store.create(
        raw_text=extracted.raw_text,
        preprocessed_text=cleaned,
        chunks=chunks,
        extraction_warnings=[],
        source_format="pasted_text",
    )

    log_event(logger, "upload_pasted_text_complete", document_id=stored.document_id, chunk_count=len(chunks))

    return UploadResponse(
        document_id=stored.document_id,
        extracted_text_preview=cleaned[:500],
        pages=1,
        chunk_count=len(chunks),
        warnings=[],
    )
