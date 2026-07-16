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

    async def fake_call_gemma(system_prompt, user_prompt, temperature=0.2, stage="unknown"):
        if stage.startswith("rewrite"):
            return _fake_rewrite_response("chunk_0")
        if stage.startswith("verify"):
            return _fake_verify_response("chunk_0")
        return "{}"

    with patch("app.services.rewrite_service.call_gemma", new=AsyncMock(side_effect=fake_call_gemma)), \
         patch("app.services.verify_service.call_gemma", new=AsyncMock(side_effect=fake_call_gemma)):
        process_resp = client.post("/process", json={"document_id": document_id, "mode": "dyslexia"})

    assert process_resp.status_code == 200
    body = process_resp.json()
    assert body["rewritten_text"] == "This is simple text."
    assert body["verification"]["is_safe"] is True


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
