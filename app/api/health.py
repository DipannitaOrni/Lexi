from fastapi import APIRouter

from app.config import get_settings
from app.schemas.common import HealthResponse
from app.services.gemma_client import GemmaAPIError, call_gemma

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    settings = get_settings()
    gemma_status = "not_configured"

    if settings.gemma_api_key:
        try:
            await call_gemma(
                system_prompt="You are a health check responder.",
                user_prompt='Reply with exactly: {"ok": true}',
                temperature=0.0,
                stage="health_check",
            )
            gemma_status = "reachable"
        except GemmaAPIError:
            gemma_status = "unreachable"

    return HealthResponse(status="ok", gemma_api=gemma_status)
