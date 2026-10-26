"""
Application Configuration Settings
Loads environment variables and sets defaults for database, security, and services.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root if present
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
load_dotenv(ROOT_DIR / ".env")


class Settings:
    PROJECT_NAME: str = "CampusPilot AI"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"
    
    # Database URL: defaults to async SQLite for effortless local dev & testing.
    # Set to postgresql+asyncpg://user:pass@localhost:5432/campuspilot in production.
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./campuspilot.db"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-123456789")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")


settings = Settings()
