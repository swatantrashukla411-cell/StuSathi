import sys
from pathlib import Path

# Add apps/api and repository root to sys.path
CUR_DIR = Path(__file__).resolve().parent
ROOT_DIR = CUR_DIR.parent.parent

for p in [str(CUR_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from src.main import app
except ImportError:
    from apps.api.src.main import app
