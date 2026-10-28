"""
Vercel Serverless Function entry point for FastAPI backend.
"""
import sys
from pathlib import Path

# Add project root directory to sys.path so apps.api imports resolve
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from apps.api.src.main import app
