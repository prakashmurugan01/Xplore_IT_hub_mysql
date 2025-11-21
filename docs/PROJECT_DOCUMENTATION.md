# Project Documentation — Xplore IT Hub

This document gives an operational view of the project: architecture, configuration, operations, and key locations in the codebase.

## Architecture (high level)
- Django project: `xplorehub/` — central settings, URL routing and WSGI/ASGI entrypoints.
- Main apps:
  - `portal/`: core application — handles user profiles, courses, materials, assignments, attendance, notifications, and reporting.
  - `newapp/`: additional app(s) — contains example models, views and tests.
- Frontend: Django templates under `templates/` and static assets under `static/`.
- Media: uploaded files stored in `media/` with subfolders per feature.

## Key files & locations
- `xplorehub/settings.py` — global settings. Inspect it for INSTALLED_APPS, DATABASES, MIDDLEWARE, and third-party integrations.
- `xplorehub/urls.py` — project URL routing. App-level urls are included from here.
- `portal/models.py` — business domain models (Profile, Course, Assignment, etc.).
- `portal/views.py`, `portal/api_views.py` — web views and API endpoints.
- `templates/` — HTML templates; `templates/*` map to app views.
- `scripts/` — developer scripts (e.g., `runserver.ps1`).

## Configuration & Environment variables
Set these in your environment or a `.env` file and load them in `settings.py`:

- `SECRET_KEY` — Django secret key
- `DEBUG` — 0 or 1
- `ALLOWED_HOSTS` — comma-separated hosts for production
- `DATABASE_URL` — production DB connection string (if using dj-database-url)
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` — email sending
- `AWS_*` or equivalent — storage for media (if using S3)

## Database & Migrations
- Development uses `db.sqlite3` by default. For production, switch to Postgres.
- Typical workflow:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
```

If you need to reset local DB (development only):

```powershell
rm db.sqlite3
python manage.py migrate
```

## Media & Static files
- Local development: uploaded files are in `media/` and served by Django when `DEBUG=True`.
- Production: configure storage backend (S3) and serve static files via `collectstatic` and a web server.

## APIs
API endpoints live mainly under `portal/api_views.py` (and possibly `portal/` submodules). To discover active routes locally you can install `django-extensions` and run:

```powershell
pip install django-extensions
python manage.py show_urls
```

For each endpoint, add documentation in this file or use an OpenAPI/DRF schema generator in future work.

## Common operational commands
- Run server: `python manage.py runserver` or `scripts\runserver.ps1`.
- Run tests: `python manage.py test`.
- Run eslint/flake8/black if configured.
- Create admin user: `python manage.py createsuperuser`.

## Troubleshooting
- Missing migrations: `python manage.py makemigrations --dry-run --verbosity 3` to inspect.
- Template errors: check the template path and `TEMPLATES` setting.
- Static files not served: run `python manage.py collectstatic` and confirm `STATIC_ROOT` is configured.
- Permission errors on media: confirm filesystem permissions.

## Backups & Data
- For SQLite: copy `db.sqlite3` (development only).
- For Postgres: use `pg_dump` and scheduled backups.

## Monitoring & Logging
- Add Sentry or similar service for error monitoring if deploying to production.
- Ensure file-based or centralized logging is configured in `settings.py`.

## Further Improvements
- Add `requirements.txt` and `requirements-dev.txt` for reproducible installs.
- Add automated test runner in CI (GitHub Actions) with lint and formatting checks.
- Add OpenAPI schema and API docs (DRF + drf-yasg or drf-spectacular).

---
This file is intended as the canonical operational summary — keep it updated when adding features or changing deployment practices.
