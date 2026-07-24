"""
Second-pass diagnostic — reproduces the EXACT payload call_llm() sends
(systemInstruction + generationConfig, no responseMimeType), so if /health
still says "unreachable" after the gemma_client.py fix, this shows the real
status code and body instead of the swallowed "unreachable" string.

Run from backend/ folder with your venv active:
    python diagnose_llm2.py
"""
import asyncio
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMMA_API_KEY", "")
API_BASE = os.getenv("GEMMA_API_BASE", "https://generativelanguage.googleapis.com/v1beta")
MODEL = os.getenv("GEMMA_CHAT_MODEL", "gemma-4-31b-it")


async def main():
    if not API_KEY:
        print("GEMMA_API_KEY is empty/not set — check .env is in this folder.")
        sys.exit(1)

    print(f"Key prefix : {API_KEY[:6]}...  (len={len(API_KEY)})")
    print(f"Base URL   : {API_BASE}")
    print(f"Model      : {MODEL}")
    print("-" * 60)

    url = f"{API_BASE}/models/{MODEL}:generateContent"

    payload = {
        "systemInstruction": {"parts": [{"text": "You are a health check responder. Output ONLY valid JSON."}]},
        "contents": [{"role": "user", "parts": [{"text": 'Reply with exactly: {"ok": true}'}]}],
        "generationConfig": {
            "temperature": 0.0,
            # deliberately NOT setting responseMimeType, matching the fixed gemma_client.py
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                url,
                headers={"Content-Type": "application/json", "x-goog-api-key": API_KEY},
                json=payload,
            )
        print(f"HTTP status: {resp.status_code}")
        print("Response body:")
        print(resp.text[:2000])

        if resp.status_code == 200:
            print("\n✅ This exact call_llm()-style payload succeeds.")
            print("   If /health STILL says unreachable, the running server process")
            print("   is not using this code — check for a stale reload, a different")
            print("   venv/site-packages, or a docker image that needs rebuilding.")
        else:
            print("\n❌ This reproduces the failure — see status/body above for the real cause.")

    except httpx.TimeoutException as e:
        print(f"❌ Timed out: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
