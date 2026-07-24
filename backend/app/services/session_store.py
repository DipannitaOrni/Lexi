"""
Lightweight session store (SQLite, shares the same DB file as the document
store) for two things that need to persist across requests but aren't tied
to a single document:

1. Per-session audio preferences (voice, speed) — "voice/speed presets
   saved per user session".
2. Per-session reading/listening progress on a document's chunks — ties
   into the frontend's ProgressSteps component.

No login/auth system exists in this hackathon build — `session_id` is any
client-generated identifier (e.g. a UUID stored in localStorage) the
frontend sends back on each request.
"""
import sqlite3
import time
from threading import Lock
from typing import List, Optional, Tuple

from app.config import get_settings

_DEFAULT_VOICE = "alloy"
_DEFAULT_SPEED = 1.0


class SessionStore:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._lock = Lock()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS session_preferences (
                    session_id TEXT PRIMARY KEY,
                    voice TEXT NOT NULL DEFAULT 'alloy',
                    speed REAL NOT NULL DEFAULT 1.0,
                    updated_at REAL NOT NULL
                )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS session_progress (
                    session_id TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    chunk_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    PRIMARY KEY (session_id, document_id, chunk_id)
                )"""
            )
            conn.commit()

    # --- preferences ---

    def get_preferences(self, session_id: str) -> Tuple[str, float]:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT voice, speed FROM session_preferences WHERE session_id = ?", (session_id,)
            ).fetchone()
        if row is None:
            return _DEFAULT_VOICE, _DEFAULT_SPEED
        return row["voice"], row["speed"]

    def set_preferences(self, session_id: str, voice: Optional[str], speed: Optional[float]) -> Tuple[str, float]:
        current_voice, current_speed = self.get_preferences(session_id)
        new_voice = voice or current_voice
        new_speed = speed if speed is not None else current_speed
        with self._lock, self._connect() as conn:
            conn.execute(
                """INSERT INTO session_preferences (session_id, voice, speed, updated_at)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(session_id) DO UPDATE SET voice=excluded.voice, speed=excluded.speed, updated_at=excluded.updated_at""",
                (session_id, new_voice, new_speed, time.time()),
            )
            conn.commit()
        return new_voice, new_speed

    # --- progress ---

    def mark_progress(self, session_id: str, document_id: str, chunk_id: str, status: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """INSERT INTO session_progress (session_id, document_id, chunk_id, status, updated_at)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(session_id, document_id, chunk_id) DO UPDATE SET status=excluded.status, updated_at=excluded.updated_at""",
                (session_id, document_id, chunk_id, status, time.time()),
            )
            conn.commit()

    def get_progress(self, session_id: str, document_id: str) -> List[str]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT chunk_id FROM session_progress WHERE session_id = ? AND document_id = ?",
                (session_id, document_id),
            ).fetchall()
        return [r["chunk_id"] for r in rows]


_settings = get_settings()
session_store = SessionStore(_settings.database_path)
