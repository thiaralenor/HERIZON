# Health Platform

Initial monorepo scaffold for a React + Vite frontend and FastAPI backend.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
uvicorn app.main:app --reload
```

The API health check is available at `http://localhost:8000/health`. Feature modules and UI components are structural placeholders and need implementation.
