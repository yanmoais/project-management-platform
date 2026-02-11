@echo off
title Project Management Platform Launcher
echo ========================================================
echo Stopping Project Management Platform Services...
echo ========================================================

:: 1. Force kill backend processes to release ports
echo Killing backend processes (Node/Python)...
taskkill /F /IM node.exe /T 2>nul
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM celery.exe /T 2>nul

:: 2. Use PowerShell to find and close windows by title
:: This is more robust than taskkill for modern Windows Terminals
echo Closing old terminal windows...
powershell -Command "Get-Process | Where-Object MainWindowTitle -Match 'FastAPI Celery Worker|FastAPI Backend|Vue Frontend' | Stop-Process -Force" 2>nul

echo Waiting for cleanup...
timeout /t 2 /nobreak >nul

echo ========================================================
echo Starting Project Management Platform Services...
echo ========================================================

:: 3. Use PowerShell to start processes minimized
:: We explicitly set the title inside the cmd command so we can find it later

echo Starting Celery Worker (Minimized)...
powershell -Command "Start-Process cmd -ArgumentList '/k title FastAPI Celery Worker && python -m celery -A backend_fastapi.core.celery_app:celery_app worker --loglevel=info --pool=gevent' -WindowStyle Minimized"

:: echo Starting FastAPI/Flask Backend (Minimized)...
:: powershell -Command "Start-Process cmd -ArgumentList '/k title Flask Backend && python backend/app.py' -WindowStyle Minimized"
echo Starting FastAPI Backend (Minimized)...
powershell -Command "Start-Process cmd -ArgumentList '/c title FastAPI Backend && python -m uvicorn backend_fastapi.main:app --host 0.0.0.0 --port 5000 --reload --no-use-colors' -WindowStyle Minimized"

echo Starting Vue Frontend (Minimized)...
powershell -Command "Start-Process cmd -ArgumentList '/c title Vue Frontend && npm run dev' -WindowStyle Minimized"

echo ========================================================
echo All services have been restarted and minimized.
echo ========================================================
timeout /t 3 >nul
exit
