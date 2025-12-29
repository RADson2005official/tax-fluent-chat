@echo off
REM ============================================================================
REM Project Restructure Script - Tax Filing Agent
REM ============================================================================
echo Starting project restructure...

REM Create core folder structure
echo Creating backend\app\core folder...
if not exist "backend\app\core" mkdir "backend\app\core"
if not exist "backend\app\schemas" mkdir "backend\app\schemas"
if not exist "backend\app\agents" mkdir "backend\app\agents"

REM Move files to core
echo Moving core files...
if exist "backend\app\config.py" move /Y "backend\app\config.py" "backend\app\core\config.py"
if exist "backend\app\database.py" move /Y "backend\app\database.py" "backend\app\core\database.py"
if exist "backend\app\security.py" move /Y "backend\app\security.py" "backend\app\core\security.py"

REM Create __init__.py for core
echo. > "backend\app\core\__init__.py"

REM Move schemas
echo Moving schemas...
if exist "backend\app\schemas.py" move /Y "backend\app\schemas.py" "backend\app\schemas\__init__.py"

REM Merge agent folders
echo Merging agent folders...
if exist "backend\app\autogen_agents\*.py" (
    for %%f in (backend\app\autogen_agents\*.py) do (
        if not "%%~nf"=="__pycache__" copy /Y "%%f" "backend\app\agents\%%~nxf"
    )
)

REM Remove duplicate main.py
echo Removing duplicate main.py...
if exist "backend\main.py" del /Q "backend\main.py"

REM Remove debug files
echo Cleaning up debug files...
if exist "backend\debug_*.py" del /Q "backend\debug_*.py"
if exist "backend\check_imports.py" del /Q "backend\check_imports.py"

REM Remove root level test files (keep in tests folder)
echo Moving test files...
if not exist "backend\tests" mkdir "backend\tests"
if exist "backend\test_*.py" (
    for %%f in (backend\test_*.py) do (
        if not exist "backend\tests\%%~nxf" move /Y "%%f" "backend\tests\%%~nxf"
    )
)

REM Remove root level verify files
if exist "verify_*.py" (
    if not exist "backend\scripts" mkdir "backend\scripts"
    for %%f in (verify_*.py) do move /Y "%%f" "backend\scripts\%%~nxf"
)

REM Remove rust-engine if exists
if exist "rust-engine" (
    echo Removing incomplete rust-engine...
    rmdir /S /Q "rust-engine"
)

REM Remove unnecessary docs
if exist "test-all-providers.html" del /Q "test-all-providers.html"
if exist "cleanup.bat" if not "%~nx0"=="cleanup.bat" del /Q "cleanup.bat"

echo.
echo ============================================================================
echo Restructure complete!
echo ============================================================================
echo.
echo Next steps:
echo 1. Run: npm install (to clean node_modules)
echo 2. Run: cd backend ^&^& pip install -r requirements.txt
echo 3. Setup .env file
echo 4. Run: docker-compose up -d
echo.
pause
