# ChoreBalancer

A local, single-user Django web app for managing shared household chores with
auto-balancing assignment.

## Idea

Household members and chores (each with an effort weight) are tracked. Each
week, the app assigns chores so every member's total effort load lands as close
to an equal target as possible, while discouraging the same person from getting
the same chore two weeks in a row.

## Status

This is a homework project scaffolded for the AI Dev Tools course. Full
implementation is planned — see [`_docs/plan.md`](_docs/plan.md).

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

Then scaffold the Django project and run it (instructions will follow once the
project is created).
