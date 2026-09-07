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

## Setup (coming soon)

Django project scaffolding, install steps, and run instructions will be added
here as the project is built.
