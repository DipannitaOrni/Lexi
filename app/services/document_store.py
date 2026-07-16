"""
In-memory document store keyed by document_id.

For a hackathon this avoids standing up a database; swap this module for a
Redis-backed implementation later without touching any API route, since
routes only ever call these functions.
"""
import uuid
from dataclasses import dataclass, field
from threading import Lock
from typing import Dict, List, Optional

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
    # cache: (mode) -> rewritten full text, per-chunk results
    rewrite_cache: Dict[str, List[dict]] = field(default_factory=dict)
    verify_cache: Dict[str, List[dict]] = field(default_factory=dict)


class DocumentStore:
    def __init__(self):
        self._store: Dict[str, StoredDocument] = {}
        self._lock = Lock()

    def create(
        self,
        raw_text: str,
        preprocessed_text: str,
        chunks: List[Chunk],
        extraction_warnings: List[PageWarning],
        source_format: str,
    ) -> StoredDocument:
        document_id = uuid.uuid4().hex
        doc = StoredDocument(
            document_id=document_id,
            raw_text=raw_text,
            preprocessed_text=preprocessed_text,
            chunks=chunks,
            extraction_warnings=extraction_warnings,
            source_format=source_format,
        )
        with self._lock:
            self._store[document_id] = doc
        return doc

    def get(self, document_id: str) -> Optional[StoredDocument]:
        return self._store.get(document_id)


# Module-level singleton — simple and sufficient for a single-process
# hackathon deployment. For multi-worker production deployment, replace
# with a shared store (Redis) so all workers see the same documents.
document_store = DocumentStore()
