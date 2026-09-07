# ChoreBalancer

A local, single-user Django web app for managing shared household chores with
auto-balancing assignment.

## Idea

Household members and chores (each with an effort weight) are tracked. Each
week, the app assigns chores so every member's total effort load lands as close
to an equal target as possible, while discouraging the same person from getting
the same chore two weeks in a row.

## Status

Homework project for the AI Dev Tools course. The app is fully implemented —
see [`_docs/plan.md`](_docs/plan.md) for the design and [`backlog.md`](backlog.md)
for the build log.

## Scope

- Members and chores management
- Auto-balancing weekly assignment (points-based fairness)
- Repeat discouragement across consecutive weeks
- Weekly checklist to mark chores completed

## Tech stack

- **Python 3.12** (managed via `uv`)
- **Django 6.1** (see `pyproject.toml`)
- SQLite for local development
- Dependencies and virtualenv managed with **uv**

## Setup

```bash
# 1. Install uv (if missing) — https://docs.astral.sh/uv/
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Sync the environment (creates .venv and installs Django per the lockfile)
uv sync
```

## Run

```bash
# Apply database migrations (first time only)
uv run python manage.py migrate

# Optional: load sample members and chores
uv run python manage.py loaddata sample

# Start the dev server
uv run python manage.py runserver
```

Then open http://127.0.0.1:8000/ and use "This week" to generate the weekly
assignments and mark them complete. The Django admin (http://127.0.0.1:8000/admin/)
is also available if you create a superuser with `createsuperuser`.

## Tests

```bash
uv run python manage.py test
```

## Production note

This app is intended for local, single-user use. `python manage.py check --deploy`
will flag the dev-only settings (`DEBUG=True`, generated `SECRET_KEY`, empty
`ALLOWED_HOSTS`, console email backend, and HTTPS-related options); hardening for
production deployment is out of scope.
