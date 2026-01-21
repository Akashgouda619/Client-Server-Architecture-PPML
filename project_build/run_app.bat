@echo off
echo Starting Backend...
:: Use python -m uvicorn to avoid PATH issues if the Scripts folder isn't in PATH
start "PPML Backend" cmd /k "cd backend && pip install -r requirements.txt && python -m uvicorn main:app --reload --port 8000"

echo Starting Frontend...
start "PPML Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo Done! Access the dashboard at http://localhost:3000
pause
