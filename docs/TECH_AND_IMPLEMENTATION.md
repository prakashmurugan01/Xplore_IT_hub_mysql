# Technology Stack & Implementation Plan

This document describes the recommended technologies for the project, why to use them, minimum versions, and a concrete step-by-step implementation plan with milestones to take the repository from prototype to a production-ready system.

**Tech Stack (recommended)**
- **Language:** Python 3.10+ (3.11 preferred for performance)
- **Web framework:** Django 4.x
- **API:** Django REST Framework (DRF) for JSON APIs
- **Real-time / WebSockets:** Django Channels 3.x (with Redis as channel layer)
- **Celery** with **Redis** or **RabbitMQ** for background tasks (email, heavy jobs)
- **Database:** PostgreSQL (production), SQLite (local dev)
- **Caching / Channels layer:** Redis
- **Storage for media:** AWS S3 (boto3, django-storages) or similar
- **WSGI / ASGI servers:** Gunicorn for WSGI, Daphne or Uvicorn for ASGI (Channels)
- **Reverse proxy / static:** Nginx (static files, proxy to app server)
- **Containerization:** Docker + Docker Compose for local reproducible stacks
- **CI/CD:** GitHub Actions (test, lint, build, deploy pipeline)
- **Testing:** pytest + pytest-django (optionally Django test runner)
- **Lint & Format:** black, isort, flake8
- **Security / Monitoring:** Sentry for error reporting; SSL via Let’s Encrypt

Minimum version suggestions and compatibility notes:
- Python 3.10+ to support typing and newer library versions.
- Use Django 4.x to ensure long-term support and compatibility with Channels 3.x.
- Celery 5.x with Redis 6.x+ or RabbitMQ 3.x+.

Repository & module mapping (how to map parts of the plan into existing structure):
- `xplorehub/` — central settings, WSGI/ASGI configuration and environment-specific settings.
- `portal/` — core domain: models, views, APIs, management commands. Grow this with subpackages, e.g., `portal/api/`, `portal/services/`.
- `newapp/` — use for experiment or new modular features; move features into domain-specific apps as they stabilize.
- `templates/`, `static/`, `media/` — frontend and assets.

Implementation Plan — milestones and tasks

Milestone 1 — Project Hygiene & Reproducible Environment (1–2 days)
- Add `requirements.txt` and `requirements-dev.txt`.
- Create `.env.example` listing required env vars and sample values.
- Add a `Makefile` or `scripts/` commands for common tasks: `setup`, `run`, `test`, `lint`.
- Add `Dockerfile` and `docker-compose.yml` for local development (Postgres + Redis + web).

Milestone 2 — Settings & Configuration (1–2 days)
- Refactor `xplorehub/settings.py` into `settings/` package: `base.py`, `dev.py`, `prod.py`.
- Add environment variable support (python-dotenv or django-environ) and config docs.

Milestone 3 — Tests & CI (2–3 days)
- Add `pytest` configuration and convert/augment tests to use pytest where helpful.
- Add basic GitHub Actions workflow: lint, test, build, and optionally run flake8/black checks.

Milestone 4 — Core Domain Stabilization (1–2 weeks depending on scope)
- Review `portal/models.py` and break into domain modules if needed (profiles, courses, assignments, attendance, notifications).
- Add model tests and migrations.
- Harden API endpoints with DRF serializers and viewsets.

Milestone 5 — Authentication, Permissions & Admin (3–5 days)
- Ensure robust auth: use Django's auth, consider `django-allauth` for social sign-in.
- Add role-based permissions and admin improvements.

Milestone 6 — Real-time & Background Processing (1–2 weeks)
- Add Channels + Redis for notifications and live dashboard updates.
- Add Celery (with Redis broker) for asynchronous tasks like emails, PDF generation, heavy reports.
- Build simple real-time feature: live notifications panel (WebSocket channel), or a lightweight chat.

Milestone 7 — Frontend polish & static handling (1 week)
- Build or improve templates and static assets.
- Add automated front-end build step if using modern toolchain (npm, webpack, Vite).

Milestone 8 — Production Hardening & Deployment (1–2 weeks)
- Containerize and prepare deployment manifests (Dockerfiles, Compose, Kubernetes manifests if needed).
- Setup CI to build images and run tests.
- Configure a PaaS or VM: e.g., DigitalOcean / AWS ECS / Heroku / GKE.
- Configure backups, logging, monitoring (Sentry), and metrics.

Detailed step-by-step checklist to implement the project (concrete commands and files)
1. Create virtual env and install pinned deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install django djangorestframework psycopg2-binary django-environ
pip freeze > requirements.txt
```

2. Add `requirements-dev.txt` for dev tools (pytest, black, flake8).
3. Create `.env.example` with keys: `SECRET_KEY`, `DEBUG=1`, `DATABASE_URL`, `REDIS_URL`, `AWS_*` placeholders.
4. Add `Dockerfile` and `docker-compose.yml` including services: `web`, `db`, `redis`, `celery`, `worker`.
5. Refactor settings into `xplorehub/settings/` and load env vars in `dev.py` and `prod.py`.
6. Implement Channels in `xplorehub/asgi.py` and add `CHANNEL_LAYERS` config.
7. Add Celery: create `celery.py` in project root and configure beat/scheduler if required.
8. Implement example API endpoints using DRF: serializers, viewsets, routers.
9. Add unit tests and integration tests for critical flows (signup, course creation, assignment upload, notifications).
10. Add GitHub Actions workflow `.github/workflows/ci.yml` that runs tests and linting.

Estimations & prioritization notes
- Start with developer experience and tests — they pay back by decreasing integration friction.
- Implement real-time features as incremental add-ons: begin with WebSocket-based lightweight notifications.
- Use managed services (RDS, ElasticCache) in production to reduce operations overhead unless you prefer self-managed infra.

Next steps (practical)
- I can generate `requirements.txt`, `.env.example`, `Dockerfile`, `docker-compose.yml`, and a starter GitHub Actions CI workflow next. Ask me which of these you want first and I will create them.
