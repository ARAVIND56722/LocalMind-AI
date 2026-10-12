import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine, Base
from app.services.retrieval.service import retrieval_service
from app.services.providers.gateway import provider_gateway

# Routers
from app.api.sessions import router as sessions_router
from app.api.chat import router as chat_router
from app.api.skills_artifacts import router as skills_artifacts_router
from app.api.models import router as models_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lenny-assistant")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize Database Schema
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized.")

    # 2. Warm up knowledge retrieval index in background
    logger.info("Initializing Lenny transcripts knowledge base...")
    retrieval_service.initialize()
    logger.info("Knowledge base index loaded and ready.")

    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade AI Assistant grounded in Lenny's Podcast & Newsletter archive.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Endpoints
@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "service": "lenny-growth-assistant",
        "version": "1.0.0"
    }

@app.get("/health/ready", tags=["Health"])
async def health_ready():
    # Database check
    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        logger.error(f"Health check DB error: {e}")

    # Retrieval index check
    if not retrieval_service.is_initialized:
        retrieval_service.initialize()
    retrieval_ok = retrieval_service.is_initialized and retrieval_service.index.corpus_size > 0

    # Ollama local check
    ollama_ok = await provider_gateway.providers["ollama"].is_available()

    ready = db_ok and retrieval_ok
    status_code = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "ready": ready,
        "database": "connected" if db_ok else "unreachable",
        "retrieval_engine": f"ready ({retrieval_service.index.corpus_size} chunks indexed)" if retrieval_ok else "not_ready",
        "ollama_local": "available" if ollama_ok else "offline"
    }

# Register API Routers
app.include_router(sessions_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(skills_artifacts_router, prefix=settings.API_V1_STR)
app.include_router(models_router, prefix=settings.API_V1_STR)
