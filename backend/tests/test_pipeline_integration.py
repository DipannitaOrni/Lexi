"""
Integration test for the /process endpoint using a mocked Gemma client, so
the pipeline wiring (extraction -> Stage 1 -> Stage 2) is verified without
any real network calls or API cost.
"""
import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _fake_rewrite_response(chunk_id: str) -> str:
    return json.dumps({"rewritten_text": "This is simple text.", "mode": "dyslexia", "chunk_id": chunk_id})


def _fake_verify_response(chunk_id: str) -> str:
    return json.dumps({"chunk_id": chunk_id, "confidence_score": 0.95, "is_safe": True, "warnings": []})


@pytest.mark.asyncio
async def test_upload_then_process_flow():
    upload_resp = client.post("/upload/text", json={"pasted_text": "This is a short original document about a permit application deadline of May 1st."})
    assert upload_resp.status_code == 200
    document_id = upload_resp.json()["document_id"]

    async def fake_call_llm(system_prompt, user_prompt, temperature=0.2, stage="unknown"):
        if stage.startswith("rewrite"):
            return _fake_rewrite_response("chunk_0")
        if stage.startswith("verify"):
            return _fake_verify_response("chunk_0")
        return "{}"

    with patch("app.services.rewrite_service.call_llm", new=AsyncMock(side_effect=fake_call_llm)), \
         patch("app.services.verify_service.call_llm", new=AsyncMock(side_effect=fake_call_llm)):
        process_resp = client.post("/process", json={"document_id": document_id, "mode": "dyslexia", "reading_level": 3})

    assert process_resp.status_code == 200
    body = process_resp.json()
    assert body["rewritten_text"] == "This is simple text."
    assert body["verification"]["is_safe"] is True
    assert "stats" in body
    assert body["stats"]["original"]["word_count"] > 0
    assert body["stats"]["rewritten"]["word_count"] > 0


def test_upload_unknown_document_id_returns_404():
    resp = client.post("/rewrite", json={"document_id": "does-not-exist", "mode": "dyslexia"})
    assert resp.status_code == 404


def test_upload_empty_text_returns_422():
    resp = client.post("/upload/text", json={"pasted_text": ""})
    assert resp.status_code in (400, 422)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_modes_endpoint_lists_seven_modes():
    resp = client.get("/modes")
    assert resp.status_code == 200
    modes = resp.json()["modes"]
    mode_ids = {m["id"] for m in modes}
    assert mode_ids == {"dyslexia", "focus", "screen_reader", "non_native", "civic", "dyscalculia", "low_vision"}


@pytest.mark.asyncio
async def test_flashcards_endpoint():
    upload_resp = client.post("/upload/text", json={"pasted_text": "The meeting is on July 1st at 3pm in Room 204."})
    document_id = upload_resp.json()["document_id"]

    async def fake_call_llm(system_prompt, user_prompt, temperature=0.2, stage="unknown"):
        return json.dumps({"flashcards": [{"question": "When is the meeting?", "answer": "July 1st at 3pm", "chunk_id": "x"}]})

    with patch("app.services.flashcards_service.call_llm", new=AsyncMock(side_effect=fake_call_llm)):
        resp = client.post("/flashcards", json={"document_id": document_id, "max_total": 5})

    assert resp.status_code == 200
    assert len(resp.json()["flashcards"]) == 1


def test_export_unknown_document_returns_404():
    resp = client.post("/export", json={"document_id": "nope", "mode": "dyslexia", "format": "txt"})
    assert resp.status_code == 404
