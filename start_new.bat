@echo off
echo Starting ARIA v2.0...
echo.

echo Starting Backend Server...
start "ARIA Backend" cmd /k "cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "ARIA Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause


