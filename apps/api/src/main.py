"""
CampusPilot AI — Application Entry Point
FastAPI modular monolith backend.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.src.core.config import settings
from apps.api.src.core.database import engine, Base
from apps.api.src.api.v1 import api_router
# Ensure all models are imported so SQLAlchemy registers them in Base.metadata
import apps.api.src.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager:
    Initializes database tables on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Teardown logic
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Voice-First Personal Academic Agent for College Students.",
    lifespan=lifespan,
)

# Cross-Origin Resource Sharing (CORS) for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend status."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API. Explore docs at /docs",
    }
