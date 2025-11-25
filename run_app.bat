@echo off
echo Starting Tax Filing System...

:: Start Backend
start "Tax Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload"

:: Start Frontend
start "Tax Frontend" cmd /k "npm run dev"

echo System started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
pause
