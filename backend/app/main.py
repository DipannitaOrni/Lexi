"""
FastAPI application entrypoint.

Registers all routers, configures CORS, structured logging, and a simple
per-IP rate limiter applied to all LLM-calling endpoints.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    ask, audio, export, flashcards, glossary, health, key_points,
    modes, process, rewrite, session, tts, upload, verify, visualize,
)
from app.config import get_settings
from app.utils.logging_config import configure_logging, get_logger
from app.utils.rate_limit import RateLimiter

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Lexi backend starting up",
        extra={"extra_fields": {"model": settings.gemma_chat_model}},
    )
    yield


app = FastAPI(
    title="Lexi — Accessibility Assistant API",
    description="AI-powered document accessibility rewriting, verification, grounded Q&A, flashcards, glossary, visualization, and audio backend.",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rate_limiter = RateLimiter(max_requests_per_minute=settings.rate_limit_per_minute)

_RATE_LIMITED_PATHS = {
    "/upload", "/upload/text", "/process", "/rewrite", "/rewrite/stream",
    "/verify", "/ask", "/flashcards", "/key-points", "/transcribe", 
    "/export", "/glossary", "/visualize",
}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in _RATE_LIMITED_PATHS:
        client_key = request.client.host if request.client else "unknown"
        if not rate_limiter.allow(client_key):
            return JSONResponse(
                status_code=429,
                content={"error": {"code": "rate_limited", "message": "Too many requests. Please slow down."}},
                headers={"Retry-After": "60"},
            )
    return await call_next(request)


app.include_router(health.router, tags=["health"])
app.include_router(upload.router, tags=["upload"])
app.include_router(process.router, tags=["process"])
app.include_router(rewrite.router, tags=["rewrite"])
app.include_router(verify.router, tags=["verify"])
app.include_router(ask.router, tags=["ask"])
app.include_router(flashcards.router, tags=["flashcards"])
app.include_router(key_points.router, tags=["key_points"])
app.include_router(glossary.router, tags=["glossary"])
app.include_router(visualize.router, tags=["visualize"])
app.include_router(audio.router, tags=["audio"])
app.include_router(tts.router, tags=["tts"])
app.include_router(session.router, tags=["session"])
app.include_router(export.router, tags=["export"])
app.include_router(modes.router, tags=["modes"])
