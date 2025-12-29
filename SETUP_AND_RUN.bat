@echo off
REM ============================================================================
REM Automated Tax Filing Agent - Complete Setup and Startup Script
REM ============================================================================
SETLOCAL EnableDelayedExpansion

echo.
echo ============================================================================
echo   AUTOMATED TAX FILING AGENT - SETUP ^& STARTUP
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Docker is running (optional)
docker ps >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker is not running or not installed.
    echo You'll need to manually setup PostgreSQL.
    echo.
    set DOCKER_AVAILABLE=0
) else (
    echo [OK] Docker is running
    set DOCKER_AVAILABLE=1
)

echo.
echo ============================================================================
echo   STEP 1: CLEAN AND RESTRUCTURE PROJECT
echo ============================================================================
echo.

REM Run cleanup if script exists
if exist cleanup_project.py (
    echo Running project cleanup...
    python cleanup_project.py
) else (
    echo [SKIP] cleanup_project.py not found
)

REM Run restructure if script exists
if exist restructure.bat (
    echo Running project restructure...
    call restructure.bat
) else (
    echo [SKIP] restructure.bat not found
)

echo.
echo ============================================================================
echo   STEP 2: BACKEND SETUP
echo ============================================================================
echo.

cd backend

REM Check if virtual environment exists
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo Installing Python dependencies (this may take a few minutes)...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Python dependencies installed

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found
    echo Please configure backend\.env before running the application
    echo A template has been created for you.
    pause
)

REM Update imports if script exists
if exist update_imports.py (
    echo Updating imports after restructure...
    python update_imports.py
)

cd ..

echo.
echo ============================================================================
echo   STEP 3: FRONTEND SETUP
echo ============================================================================
echo.

REM Check if node_modules exists
if not exist node_modules (
    echo Installing Node.js dependencies (this may take a few minutes)...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install Node.js dependencies
        pause
        exit /b 1
    )
    echo [OK] Node.js dependencies installed
) else (
    echo [OK] Node modules already installed
    echo Run 'npm install' manually if you need to update dependencies
)

echo.
echo ============================================================================
echo   STEP 4: DATABASE SETUP
echo ============================================================================
echo.

if !DOCKER_AVAILABLE! == 1 (
    echo Starting PostgreSQL with pgvector...
    docker-compose up -d postgres
    if errorlevel 1 (
        echo [ERROR] Failed to start PostgreSQL
        pause
        exit /b 1
    )
    
    echo Waiting for PostgreSQL to be ready...
    timeout /t 10 /nobreak >nul
    
    echo [OK] PostgreSQL started
    echo.
    echo Database credentials:
    echo   Host: localhost:5432
    echo   Database: tax_filing_db
    echo   User: taxagent
    echo   Password: taxagent_secure_password_2024
    echo.
    echo pgAdmin available at: http://localhost:5050
    echo   Email: admin@taxagent.com
    echo   Password: admin123
) else (
    echo [SKIP] Docker not available - manual PostgreSQL setup required
    echo Please ensure PostgreSQL 16+ with pgvector extension is installed
)

echo.
echo ============================================================================
echo   STEP 5: DATABASE MIGRATIONS
echo ============================================================================
echo.

cd backend
call venv\Scripts\activate.bat

REM Check if alembic is configured
if exist alembic.ini (
    echo Running database migrations...
    alembic upgrade head
    if errorlevel 1 (
        echo [WARNING] Migration failed - database might need manual setup
    ) else (
        echo [OK] Database migrations completed
    )
) else (
    echo [SKIP] Alembic not configured
)

cd ..

echo.
echo ============================================================================
echo   SETUP COMPLETE!
echo ============================================================================
echo.
echo To start the application:
echo   1. Backend:  cd backend ^&^& venv\Scripts\activate ^&^& python main.py
echo   2. Frontend: npm run dev
echo.
echo Access points:
echo   - Frontend:     http://localhost:8080
echo   - Backend API:  http://localhost:8000/api/docs
echo   - Health Check: http://localhost:8000/api/health
echo   - PostgreSQL:   localhost:5432
echo   - pgAdmin:      http://localhost:5050
echo.
echo ============================================================================
echo.

REM Ask if user wants to start the application
set /p START_NOW="Do you want to start the application now? (Y/N): "
if /i "%START_NOW%"=="Y" (
    echo.
    echo Starting backend and frontend...
    echo Backend will start in this window
    echo Frontend will open in a new window
    echo.
    
    REM Start frontend in new window
    start "Tax Filing Agent - Frontend" cmd /k "npm run dev"
    
    REM Start backend in this window
    cd backend
    call venv\Scripts\activate.bat
    python main.py
) else (
    echo.
    echo You can start the application manually later.
    echo.
    pause
)

ENDLOCAL
