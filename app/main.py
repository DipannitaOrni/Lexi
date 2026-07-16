"""
FastAPI application entrypoint.

Registers all routers, configures CORS, structured logging, and a simple
per-IP rate limiter applied to all Gemma-calling endpoints.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import ask, health, process, rewrite, upload, verify
from app.config import get_settings
from app.utils.logging_config import configure_logging, get_logger
from app.utils.rate_limit import RateLimiter

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Accessibility Assistant backend starting up",
        extra={"extra_fields": {"model": settings.gemma_model_name}},
    )
    yield


app = FastAPI(
    title="Accessibility Assistant API",
    description="AI-powered document accessibility rewriting, verification, and grounded Q&A backend.",
    version="1.0.0",
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

_RATE_LIMITED_PATHS = {"/upload", "/upload/text", "/process", "/rewrite", "/verify", "/ask"}


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
