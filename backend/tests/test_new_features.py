"""
Tests for the second feature batch: new modes, glossary, visualization,
session preferences/progress, and timed TTS. LLM calls and TTS/embeddings
are mocked so these run with no network access or API cost.
"""
import base64
import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _upload_sample():
    resp = client.post("/upload/text", json={"pasted_text": "Group A had 120 approvals. Group B had 45 approvals."})
    return resp.json()["document_id"]


def test_modes_includes_new_modes():
    resp = client.get("/modes")
    mode_ids = {m["id"] for m in resp.json()["modes"]}
    assert "dyscalculia" in mode_ids
    assert "low_vision" in mode_ids


@pytest.mark.asyncio
async def test_rewrite_with_dyscalculia_mode():
    document_id = _upload_sample()

    async def fake_call_llm(system_prompt, user_prompt, temperature=0.2, stage="unknown"):
        return json.dumps({"rewritten_text": "Group A had more approvals than Group B.", "mode": "dyscalculia", "chunk_id": "chunk_0"})

    with patch("app.services.rewrite_service.call_llm", new=AsyncMock(side_effect=fake_call_llm)):
        resp = client.post("/rewrite", json={"document_id": document_id, "mode": "dyscalculia", "reading_level": 3})

    assert resp.status_code == 200
    assert "Group A" in resp.json()["rewritten_text"]


@pytest.mark.asyncio
async def test_glossary_endpoint():
    document_id = _upload_sample()

    async def fake_call_llm(system_prompt, user_prompt, temperature=0.2, stage="unknown"):
        return json.dumps({"terms": [{"term": "approvals", "definition": "requests that were accepted", "chunk_id": "x"}]})

    with patch("app.services.glossary_service.call_llm", new=AsyncMock(side_effect=fake_call_llm)):
        resp = client.post("/glossary", json={"document_id": document_id, "max_terms": 10})

    assert resp.status_code == 200
    assert len(resp.json()["terms"]) == 1


@pytest.mark.asyncio
async def test_visualize_endpoint_bar_chart():
    document_id = _upload_sample()

    async def fake_call_llm(system_prompt, user_prompt, temperature=0.2, stage="unknown"):
        return json.dumps({
            "visualization_type": "bar_chart",
            "title": "Approvals by Group",
            "mermaid_code": None,
            "chart_data": {"labels": ["Group A", "Group B"], "values": [120, 45], "unit": "approvals"},
            "explanation": "The text compares two numeric groups.",
        })

    with patch("app.services.visualize_service.call_llm", new=AsyncMock(side_effect=fake_call_llm)):
        resp = client.post("/visualize", json={"document_id": document_id})

    assert resp.status_code == 200
    body = resp.json()
    assert body["visualization_type"] == "bar_chart"
    assert body["chart_data"]["values"] == [120, 45]


def test_visualize_unknown_document_404():
    resp = client.post("/visualize", json={"document_id": "nope"})
    assert resp.status_code == 404


def test_session_preferences_round_trip():
    put_resp = client.put("/session/preferences", json={"session_id": "sess-1", "voice": "nova", "speed": 1.25})
    assert put_resp.status_code == 200
    assert put_resp.json()["voice"] == "nova"
    assert put_resp.json()["speed"] == 1.25

    get_resp = client.get("/session/preferences", params={"session_id": "sess-1"})
    assert get_resp.status_code == 200
    assert get_resp.json()["voice"] == "nova"


def test_progress_tracking_round_trip():
    document_id = _upload_sample()

    post_resp = client.post("/progress", json={
        "session_id": "sess-2", "document_id": document_id, "chunk_id": "does-not-need-to-exist", "status": "read",
    })
    assert post_resp.status_code == 200
    assert post_resp.json()["percent_complete"] >= 0

    get_resp = client.get("/progress", params={"session_id": "sess-2", "document_id": document_id})
    assert get_resp.status_code == 200
    assert "does-not-need-to-exist" in get_resp.json()["completed_chunk_ids"]


@pytest.mark.asyncio
async def test_tts_timed_returns_word_timings():
    async def fake_tts(text, voice=None, speed=1.0):
        return b"fake-mp3-bytes"

    with patch("app.api.audio.text_to_speech", new=AsyncMock(side_effect=fake_tts)):
        resp = client.post("/tts/timed", json={"text": "Hello there friend.", "speed": 1.0})

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["words"]) == 3
    assert base64.b64decode(body["audio_base64"]) == b"fake-mp3-bytes"
    assert body["duration_seconds"] > 0
