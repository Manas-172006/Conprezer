# Conprezer

Privacy-first local MVP for DOCX-to-PDF conversion and PDF compression. It includes a FastAPI API, MySQL persistence, a polling worker, and a React/Vite interface.

## Run locally with Docker Compose

1. Copy `.env.example` to `.env` and replace the placeholder passwords and `SECRET_KEY`. Use a long random secret, for example generated with `openssl rand -hex 32`.
2. From this directory run `docker compose up --build`.
3. Open <http://localhost:3000>. API health is at <http://localhost:8000/health>.

The application creates accounts locally. After signing in, use **DOCX → PDF** or **Compress PDF**. Jobs are queued and processed by the worker. History and downloads require authentication. Uploads are limited to 25 MiB.

## Scope and limitations

- DOCX-to-PDF converts paragraph text; advanced Word layout, images, and embedded objects are not preserved.
- PDF compression uses Ghostscript's ebook preset and may alter quality.
- The development cookie is HTTP-only and `SameSite=Lax`; configure HTTPS and secure cookies before production deployment. Add rate limiting, CSRF defenses, retention/cleanup, and production-grade monitoring before exposing the service publicly.
- Uploaded and generated files are held in a Docker volume and are not automatically deleted.

## Backend development

The API runs Alembic migrations before starting. To run backend checks or the API outside Docker, configure the environment variables in `.env`, install `backend/requirements.txt`, and run Alembic plus Uvicorn from `backend/`.
