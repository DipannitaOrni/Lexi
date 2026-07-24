"""
PUT /session/preferences — save per-session voice/speed presets.
GET /session/preferences — fetch a session's current preferences.

POST /progress — mark a document chunk as read or listened to.
GET  /progress — fetch a session's completion state for a document, for
the ProgressSteps.jsx frontend component.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.session_schema import (
    PreferencesResponse,
    PreferencesUpdateRequest,
    ProgressResponse,
    ProgressUpdateRequest,
)
from app.services.document_store import document_store
from app.services.session_store import session_store

router = APIRouter()


@router.put("/session/preferences", response_model=PreferencesResponse)
async def update_preferences(body: PreferencesUpdateRequest):
    voice, speed = session_store.set_preferences(body.session_id, body.voice, body.speed)
    return PreferencesResponse(session_id=body.session_id, voice=voice, speed=speed)


@router.get("/session/preferences", response_model=PreferencesResponse)
async def get_preferences(session_id: str):
    voice, speed = session_store.get_preferences(session_id)
    return PreferencesResponse(session_id=session_id, voice=voice, speed=speed)


@router.post("/progress", response_model=ProgressResponse)
async def update_progress(body: ProgressUpdateRequest):
    document = document_store.get(body.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    session_store.mark_progress(body.session_id, body.document_id, body.chunk_id, body.status)
    completed = session_store.get_progress(body.session_id, body.document_id)
    total = len(document.chunks)
    percent = round(100 * len(completed) / total, 1) if total else 0.0

    return ProgressResponse(
        document_id=body.document_id, total_chunks=total,
        completed_chunk_ids=completed, percent_complete=percent,
    )


@router.get("/progress", response_model=ProgressResponse)
async def get_progress(session_id: str, document_id: str):
    document = document_store.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "document_not_found", "message": "Unknown document_id."}})

    completed = session_store.get_progress(session_id, document_id)
    total = len(document.chunks)
    percent = round(100 * len(completed) / total, 1) if total else 0.0

    return ProgressResponse(
        document_id=document_id, total_chunks=total,
        completed_chunk_ids=completed, percent_complete=percent,
    )
