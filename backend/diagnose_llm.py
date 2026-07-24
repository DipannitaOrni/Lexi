"""
Standalone diagnostic for the "llm_api": "unreachable" status from /health.

Run this from the backend/ folder (same place as .env) with your venv active:

    python diagnose_llm.py

It reproduces exactly what app/services/gemma_client.py does for the health
check, but WITHOUT swallowing the error, so you can see the real HTTP status
code and response body from Google instead of just "unreachable".
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

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                url,
                headers={"Content-Type": "application/json", "x-goog-api-key": API_KEY},
                json={
                    "contents": [{"role": "user", "parts": [{"text": "Reply with exactly: OK"}]}],
                },
            )
        print(f"HTTP status: {resp.status_code}")
        print("Response body:")
        print(resp.text[:2000])

        if resp.status_code == 200:
            print("\n✅ Call succeeded — the key/model/base URL are fine.")
            print("   If /health still says 'unreachable', the bug is likely in")
            print("   how your running server process loads env vars (wrong cwd,")
            print("   stale reload, or a different .env being picked up).")
        elif resp.status_code in (401, 403):
            print("\n❌ Auth error. Common causes:")
            print("   - Key revoked/expired, or copy-pasted with extra whitespace")
            print("   - Key is restricted to a different API/service")
            print("   - Known Google-side issue: newly-issued 'AQ.' auth-format keys")
            print("     occasionally get rejected here even though the docs show")
            print("     this exact call working — try regenerating a fresh key at")
            print("     https://aistudio.google.com/apikey and re-testing.")
        elif resp.status_code == 404:
            print(f"\n❌ Model '{MODEL}' not found at this API base — check spelling")
        elif resp.status_code == 429:
            print("\n❌ Rate limited / quota exceeded.")
        elif resp.status_code >= 500:
            print("\n❌ Google-side server error — likely transient, retry later.")

    except httpx.ConnectError as e:
        print(f"❌ Could not connect at all: {e}")
        print("   This means the request never reached Google — check your network,")
        print("   VPN/proxy, or firewall rules for generativelanguage.googleapis.com.")
    except httpx.TimeoutException as e:
        print(f"❌ Timed out: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
