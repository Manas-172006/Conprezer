# Conprezer

Privacy-first local MVP for DOCX-to-PDF conversion and PDF compression. It includes a FastAPI API, MySQL persistence, a polling worker, and a React/Vite interface.

## Run locally with Docker Compose

1. Copy `.env.example` to `.env` and replace all placeholder passwords and `SECRET_KEY`. Use a long random secret, for example generated with `openssl rand -hex 32`.
2. Set `GUEST_MODE=true` to enable guest uploads. Guest jobs are retained for `GUEST_JOB_TTL_HOURS` (24 by default), then the worker removes their database records and files.
3. From this directory run `docker compose up --build`.
4. Open <http://localhost:3000>. API health is at <http://localhost:8000/health>.

The application seeds two local demo accounts and one completed sample conversion. The seed service generates new passwords each time it runs; see them with `docker compose logs seed`. Do not expose this development setup publicly. After signing in or choosing **Continue as guest**, use **DOCX → PDF** or **Compress PDF**. Jobs are queued and processed by the worker. Guest sessions use a short-lived HTTP-only cookie and can access only their own jobs; guest job metadata and files expire together. Uploads are limited to 25 MiB.

## Scripts

Run these commands from the repository root with the backend dependencies installed and the relevant services configured:

- `python scripts/init_db.py` applies Alembic migrations.
- `python scripts/run_worker.py` starts the polling conversion worker.
- `python scripts/seed_demo_data.py` creates demo accounts and a sample completed job (passwords are generated and printed each run).
- `pytest scripts/test_convert.py` runs an API smoke test. Start the API and worker first, enable `GUEST_MODE=true`, and install `backend/requirements-dev.txt`. Set `CONPREZER_API_URL` to target a different API address.

## Scope and limitations

- DOCX-to-PDF converts paragraph text; advanced Word layout, images, and embedded objects are not preserved.
- PDF compression uses Ghostscript's ebook preset and may alter quality.
- Guest jobs are temporary and tied to a browser cookie; clearing the cookie loses access before the TTL.
- Development auth and guest cookies are HTTP-only and `SameSite=Lax`; configure HTTPS and secure cookies before production deployment. Add rate limiting, CSRF defenses, retention/cleanup, and production-grade monitoring before exposing the service publicly.
- Authenticated uploads and generated files are held in a Docker volume and are not automatically deleted.

## Backend development

The API runs Alembic migrations before starting. To run backend checks or the API outside Docker, configure the environment variables in `.env`, install `backend/requirements.txt`, and run Alembic plus Uvicorn from `backend/`.
