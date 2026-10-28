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
    Initializes database tables and auto-seeds initial curriculum if database is fresh.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Auto-seed default student profile and curriculum if database is newly initialized
    try:
        from apps.api.src.core.database import AsyncSessionLocal
        from apps.api.src.models.academic import User
        from apps.api.src.api.v1.auth import initialize_new_student_curriculum
        from sqlalchemy import select

        async with AsyncSessionLocal() as session:
            check_u = await session.execute(select(User).limit(1))
            if not check_u.scalar_one_or_none():
                default_user = User(
                    full_name="Swatantra Shukla",
                    email="24030320@quantumuniversity.edu.in",
                    program="B.Tech Computer Science & Engineering (AI/ML)",
                )
                session.add(default_user)
                await session.flush()
                await initialize_new_student_curriculum(db=session, user=default_user, sem_num=5)
    except Exception as e:
        print(f"Startup seeding notice: {e}")

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

# Register API v1 routes at both /api/v1 and /v1 for dual proxy / services compatibility
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router, prefix="/v1")


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
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
