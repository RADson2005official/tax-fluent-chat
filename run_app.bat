@echo off
echo ==========================================
echo   Tax Filing System - Startup Script
echo ==========================================
echo.

:: Check if PostgreSQL is running
echo [1/4] Checking PostgreSQL...
sc query postgresql-x64-16 >nul 2>&1
if errorlevel 1 (
    echo WARNING: PostgreSQL service may not be running
    echo Run: net start postgresql-x64-16
) else (
    echo PostgreSQL is running
)
echo.

:: Start Backend
echo [2/4] Starting Backend (FastAPI)...
start "Tax Backend - FastAPI" cmd /k "cd /d %~dp0backend && if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) && python main.py"
timeout /t 3 /nobreak >nul
echo.

:: Start Frontend
echo [3/4] Starting Frontend (Vue)...
start "Tax Frontend - Vue" cmd /k "cd /d %~dp0 && npm run dev"
timeout /t 3 /nobreak >nul
echo.

:: Display URLs
echo [4/4] System Started!
echo ==========================================
echo   Frontend: http://localhost:8080
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/api/docs
echo ==========================================
echo.
echo Press any key to close this window...
pause >nul
