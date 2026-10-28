@echo off
title CampusPilot AI - 1-Click Live Launcher
echo ========================================================
echo       Starting CampusPilot AI (Local + Cloud Live)
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Starting FastAPI Backend on port 8001...
start "CampusPilot Backend (8001)" cmd /k ".venv\Scripts\python.exe run_backend.py"

echo [2/3] Starting Next.js Web Dashboard on port 3000...
start "CampusPilot Frontend (3000)" cmd /k "cd apps\web && "C:\Users\shukl\AppData\Local\Microsoft\WinGet\Packages\OpenJS.NodeJS.LTS_Microsoft.Winget.Source_8wekyb3d8bbwe\node-v24.17.0-win-x64\node.exe" node_modules\next\dist\bin\next dev -p 3000"

echo [3/3] Creating Live Public Cloudflare HTTPS Tunnel...
echo.
echo Please wait 5 seconds while servers initialize...
timeout /t 5 /nobreak >nul

echo Starting Public Tunnel... Look for the trycloudflare.com URL below:
echo ========================================================
cloudflared.exe tunnel --url http://localhost:3000
pause
