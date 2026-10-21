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
# Buea Health Platform

Two products on one backend:

1. **Freelance specialist discovery** — patients in Buea find specialists (hospital-affiliated or freelance) by neighborhood.
2. **Emergency dispatch (Path A / demo)** — simulated ambulance assignment and tracking, ready for pilot conversations with hospitals.

Both share auth, profiles, hospitals, and doctors.

## Stack

- **Backend**: FastAPI + Pydantic v2, Python 3.11+
- **Database + auth + storage**: Supabase (Postgres)
- **Migrations**: `supabase/migrations/`
- **Tests**: pytest (unit + integration), pgTAP (RLS)

## Prerequisites

- Python 3.11+
- Docker (optional, for containerized backend)
- Supabase CLI: `npm i -g supabase` (or `brew install supabase/tap/supabase`)
- `uv` (recommended) or `pip`

## Local setup

```bash
# 1. install backend deps
cd backend
uv sync --extra dev           # or: pip install -e ".[dev]"

# 2. start local Supabase (Postgres + Auth + PostgREST + Storage on :54321)
supabase start

# 3. apply migrations
supabase db reset

# 4. copy env
cp .env.example .env
# set SUPABASE_URL and keys from `supabase status`

# 5. run
uvicorn app.main:app --reload