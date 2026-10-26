@echo off
echo ========================================================
echo        Starting CampusPilot AI Full-Stack Platform
echo ========================================================
echo.

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "CampusPilot Backend (FastAPI)" cmd /k ".venv\Scripts\activate && uvicorn apps.api.src.main:app --reload --port 8000"

timeout /t 2 /nobreak > nul

echo [2/2] Starting Next.js Frontend on http://localhost:3000 ...
start "CampusPilot Frontend (Next.js)" cmd /k "cd apps\web && npm run dev"

echo.
echo ========================================================
echo  All systems running!
echo  - Frontend: http://localhost:3000
echo  - API Docs: http://127.0.0.1:8000/docs
echo ========================================================
pause
