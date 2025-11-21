# Developer Guide — Xplore IT Hub

This guide helps a new developer get the project running locally and contribute safely.

## Local development setup (Windows PowerShell)
1. Clone the repo and open a PowerShell terminal in the project root.
2. Create and activate virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -U pip setuptools wheel
if (Test-Path requirements.txt) { pip install -r requirements.txt }
```

4. Apply migrations and create superuser:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

## Running & Debugging
- Run server: `python manage.py runserver` or `scripts\runserver.ps1`.
- Debugging in VS Code: create a Django debug configuration and ensure `DJANGO_SETTINGS_MODULE` is set.

## Tests
- Run the entire test suite: `python manage.py test`.
- Run tests for a single app: `python manage.py test portal`.
- Use `pytest` if configured; it can be faster and has many useful plugins.

## Adding features
1. Add models in the relevant app's `models.py`.
2. Create migrations: `python manage.py makemigrations`.
3. Write tests alongside new code (prefer `tests.py` or `tests/` subpackage).
4. Implement views, templates, API endpoints as needed.

## Coding conventions
- Follow existing code style and naming. Use descriptive function and variable names.
- Use `black` for formatting and `flake8` for linting where possible.

## Git workflow
- Branch from `main`: `feature/your-feature-name`.
- Keep PRs small and focused; include tests.
- Rebase or squash before merging if required by the repository maintainers.

## CI / Automation suggestions
- Add GitHub Actions or another CI to run tests, lint and security checks on PRs.
- Add a `requirements-dev.txt` for developer tools: `pytest`, `black`, `flake8`, `django-extensions`.

## Helpful scripts in this repo
- `scripts/runserver.ps1` — convenience script to run server on Windows
- `scripts/test_*.py` — repository contains several test helpers; inspect them when working on tests

## Notes on extending APIs
- Prefer using Django REST Framework (DRF) if you plan to expand API coverage.
- Add serializers, viewsets and routers for clear, testable APIs.

## When you get stuck
- Re-run failing tests locally and inspect tracebacks.
- Check `xplorehub/settings.py` for environment or configuration mismatches.
- Search for related templates and view names under `templates/` and `portal/`.

---
If you'd like, I can also add a `requirements.txt` and a sample `.env.example` showing recommended env variables.
