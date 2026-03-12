@echo off
title Project Management Platform Launcher

:: Get project dir dynamically and strip trailing backslash
set "PROJ_DIR=%~dp0"
set "PROJ_DIR=%PROJ_DIR:~0,-1%"
set "VENV_PYTHON=%PROJ_DIR%\venv\Scripts\python.exe"

echo ========================================================
echo Stopping Project Management Platform Services...
echo ========================================================

:: 1. Force kill backend processes to release ports
echo Killing backend processes (Node/Python)...
taskkill /F /IM node.exe /T 2>nul
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM celery.exe /T 2>nul

:: 2. Use PowerShell to find and close windows by title
echo Closing old terminal windows...
powershell -Command "Get-Process | Where-Object MainWindowTitle -Match 'FastAPI Celery Worker|FastAPI Celery Beat|FastAPI Backend|Vue Frontend' | Stop-Process -Force" 2>nul

echo Waiting for cleanup...
timeout /t 2 /nobreak >nul

echo ========================================================
echo Starting Project Management Platform Services...
echo ========================================================

echo Starting Celery Worker (Minimized)...
start "FastAPI Celery Worker" /MIN /D "%PROJ_DIR%" cmd /k "%VENV_PYTHON% -m celery -A backend_fastapi.core.celery_app:celery_app worker --loglevel=info --pool=eventlet"

echo Starting Celery Beat (Minimized)...
start "FastAPI Celery Beat" /MIN /D "%PROJ_DIR%" cmd /k "%VENV_PYTHON% -m celery -A backend_fastapi.core.celery_app:celery_app beat --loglevel=info"

echo Starting FastAPI Backend (Minimized)...
start "FastAPI Backend" /MIN /D "%PROJ_DIR%" cmd /k "%VENV_PYTHON% -m uvicorn backend_fastapi.main:app --host 0.0.0.0 --port 5000 --reload --no-use-colors"

echo Starting Vue Frontend (Minimized)...
start "Vue Frontend" /MIN /D "%PROJ_DIR%" cmd /k "npm run dev"

echo ========================================================
echo All services have been restarted and minimized.
echo ========================================================
timeout /t 3 >nul
exit
