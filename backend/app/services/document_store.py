"""
SQLite-backed document store keyed by document_id.

Persists uploaded documents (and their rewrite/verify/embedding caches)
across server restarts — important both for production robustness and so a
demo doesn't lose uploaded documents if the server needs a restart mid-run.

Same public interface as the earlier in-memory version (`create`, `get`)
so no calling code elsewhere needed to change.
"""
import json
import sqlite3
import uuid
from dataclasses import dataclass, field, asdict
from threading import Lock
from typing import Dict, List, Optional

from app.config import get_settings
from app.services.extraction.base import PageWarning
from app.utils.chunking import Chunk


@dataclass
class StoredDocument:
    document_id: str
    raw_text: str
    preprocessed_text: str
    chunks: List[Chunk]
    extraction_warnings: List[PageWarning]
    source_format: str
    rewrite_cache: Dict[str, List[dict]] = field(default_factory=dict)
    verify_cache: Dict[str, List[dict]] = field(default_factory=dict)
    # chunk_id -> embedding vector, populated lazily by qa_service on first use
    chunk_embeddings: Dict[str, List[float]] = field(default_factory=dict)


def _row_to_document(row: sqlite3.Row) -> StoredDocument:
    chunks = [Chunk(**c) for c in json.loads(row["chunks"])]
    warnings = [PageWarning(**w) for w in json.loads(row["extraction_warnings"])]
    return StoredDocument(
        document_id=row["document_id"],
        raw_text=row["raw_text"],
        preprocessed_text=row["preprocessed_text"],
        chunks=chunks,
        extraction_warnings=warnings,
        source_format=row["source_format"],
        rewrite_cache=json.loads(row["rewrite_cache"]),
        verify_cache=json.loads(row["verify_cache"]),
        chunk_embeddings=json.loads(row["chunk_embeddings"]),
    )


class DocumentStore:
    """
    Thread-safe SQLite-backed store. Each StoredDocument is serialized as
    JSON columns — simple and sufficient at hackathon scale, with a schema
    that's trivial to migrate to Postgres later if needed (same shape).
    """

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
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    raw_text TEXT NOT NULL,
                    preprocessed_text TEXT NOT NULL,
                    chunks TEXT NOT NULL,
                    extraction_warnings TEXT NOT NULL,
                    source_format TEXT NOT NULL,
                    rewrite_cache TEXT NOT NULL DEFAULT '{}',
                    verify_cache TEXT NOT NULL DEFAULT '{}',
                    chunk_embeddings TEXT NOT NULL DEFAULT '{}',
                    created_at REAL NOT NULL
                )
                """
            )
            conn.commit()

    def create(
        self,
        raw_text: str,
        preprocessed_text: str,
        chunks: List[Chunk],
        extraction_warnings: List[PageWarning],
        source_format: str,
    ) -> StoredDocument:
        import time

        document_id = uuid.uuid4().hex
        with self._lock, self._connect() as conn:
            conn.execute(
                """INSERT INTO documents
                   (document_id, raw_text, preprocessed_text, chunks, extraction_warnings,
                    source_format, rewrite_cache, verify_cache, chunk_embeddings, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, '{}', '{}', '{}', ?)""",
                (
                    document_id,
                    raw_text,
                    preprocessed_text,
                    json.dumps([asdict(c) for c in chunks]),
                    json.dumps([asdict(w) for w in extraction_warnings]),
                    source_format,
                    time.time(),
                ),
            )
            conn.commit()

        return StoredDocument(
            document_id=document_id,
            raw_text=raw_text,
            preprocessed_text=preprocessed_text,
            chunks=chunks,
            extraction_warnings=extraction_warnings,
            source_format=source_format,
        )

    def get(self, document_id: str) -> Optional[StoredDocument]:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()
        return _row_to_document(row) if row else None

    def save(self, document: StoredDocument) -> None:
        """Persists mutations made to a StoredDocument's caches back to disk."""
        with self._lock, self._connect() as conn:
            conn.execute(
                """UPDATE documents SET
                     rewrite_cache = ?, verify_cache = ?, chunk_embeddings = ?
                   WHERE document_id = ?""",
                (
                    json.dumps(document.rewrite_cache),
                    json.dumps(document.verify_cache),
                    json.dumps(document.chunk_embeddings),
                    document.document_id,
                ),
            )
            conn.commit()


_settings = get_settings()
document_store = DocumentStore(_settings.database_path)
