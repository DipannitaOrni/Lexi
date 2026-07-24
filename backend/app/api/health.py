from fastapi import APIRouter

from app.config import get_settings
from app.schemas.common import HealthResponse
from app.services.gemma_client import LLMAPIError, call_llm

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    settings = get_settings()
    llm_status = "not_configured"

    if settings.gemma_api_key:
        try:
            await call_llm(
                system_prompt="You are a health check responder. Output ONLY valid JSON.",
                user_prompt='Reply with exactly: {"ok": true}',
                temperature=0.0,
                stage="health_check",
            )
            llm_status = "reachable"
        except LLMAPIError as exc:
            # TEMPORARY: surface the real error instead of swallowing it, so we
            # can see what's actually failing. Revert this once diagnosed.
            llm_status = f"unreachable: {type(exc).__name__}: {exc} (status_code={getattr(exc, 'status_code', None)})"

    return HealthResponse(status="ok", llm_api=llm_status)
