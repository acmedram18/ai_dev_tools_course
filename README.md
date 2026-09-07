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

- **Python 3.12** (managed with pyenv)
- **Django 6.1** (see `requirements.txt`)
- SQLite for local development

## Setup

```bash
# 1. Ensure pyenv has Python 3.12 installed
pyenv install 3.12   # once, if missing

# 2. (One-time) point the repo at Python 3.12
pyenv local 3.12

# 3. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

Then scaffold the Django project and run it (instructions will follow once the
project is created).
