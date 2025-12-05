@echo off
start cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3
start cmd /k "cd frontend && npm run dev"
