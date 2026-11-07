# Conprezer

Privacy-first local MVP for DOCX-to-PDF conversion and PDF compression. It includes a FastAPI API, MySQL persistence, a polling worker, and a React/Vite interface.

## Run locally with Docker Compose

1. Copy `.env.example` to `.env` and replace all placeholder passwords and `SECRET_KEY`. Use a long random secret, for example generated with `openssl rand -hex 32`.
2. Set `GUEST_MODE=true` to enable guest uploads. Guest jobs are retained for `GUEST_JOB_TTL_HOURS` (24 by default), then the worker removes their database records and files.
3. From this directory run `docker compose up --build`.
4. Open <http://localhost:3000>. API health is at <http://localhost:8000/health>.

The application seeds two local demo accounts with placeholder password hashes and one completed sample job with a dummy output path. These accounts are for UI development, not login. Do not expose this development setup publicly. After signing in or choosing **Continue as guest**, use **DOCX → PDF** or **Compress PDF**. Jobs are queued and processed by the worker. Guest sessions use a short-lived HTTP-only cookie and can access only their own jobs; guest job metadata and files expire together. Uploads are limited to 25 MiB.

## Guest / anonymous usage

Set `GUEST_MODE=true` in `.env` and restart the services to enable guest use; it is disabled by default. Guests can convert DOCX files and compress PDFs without creating an account or writing a user row. There is no per-guest conversion-count quota, though each upload is still limited to 25 MiB. Guest job records, files, and their temporary download URLs expire after 24 hours by default (`GUEST_JOB_TTL_HOURS` can change the retention period). Guest status and download links are tied to the browser's HTTP-only guest cookie and cannot be used after that session expires or the cookie is cleared.

## CLI utilities

Run these commands from the repository root with the backend dependencies installed and the relevant services configured:

- `python scripts/init_db.py` applies Alembic migrations.
- `python scripts/run_worker.py` starts the polling conversion worker.
- `pytest scripts/test_convert.py` uploads `tests/sample.docx` and verifies the generated PDF. Start the API and worker first; guest mode must be enabled for the guest branch of this test. Install `backend/requirements-dev.txt` and set `CONPREZER_API_URL` to target a different API address.
- `python scripts/seed_demo_data.py` inserts the two placeholder demo accounts and a completed sample job.
- `python scripts/cleanup_expired_jobs.py` deletes expired conversion records and their input/output files, then prints the number of records removed.

## Scope and limitations

- DOCX-to-PDF converts paragraph text; advanced Word layout, images, and embedded objects are not preserved.
- PDF compression uses Ghostscript's ebook preset and may alter quality.
- Guest jobs are temporary and tied to a browser cookie; clearing the cookie loses access before the TTL.
- Development auth and guest cookies are HTTP-only and `SameSite=Lax`; configure HTTPS and secure cookies before production deployment. Add rate limiting, CSRF defenses, retention/cleanup, and production-grade monitoring before exposing the service publicly.
- Authenticated uploads and generated files are held in a Docker volume and are not automatically deleted.

## Backend development

The API runs Alembic migrations before starting. To run backend checks or the API outside Docker, configure the environment variables in `.env`, install `backend/requirements.txt`, and run Alembic plus Uvicorn from `backend/`.
