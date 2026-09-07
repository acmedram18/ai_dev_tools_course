# Backlog

Ordered by dependency. Small tasks, each with a clear done-criterion.

## 1. Scaffold Django project
- [x] `django-admin startproject` inside the repo (project root), using the
      repo venv (`source .venv/bin/activate` first).
- [x] Create the `chores` app and register it in `INSTALLED_APPS`.
- [x] Verify `python manage.py check` and `migrate` run clean.
- [x] **Done when:** dev server starts and the Django welcome page renders.

## 2. Data models
- [ ] Define `Member` (name), `Chore` (name, weight 1–5),
      `Assignment` (chore, member, week, completed).
- [ ] Add constraints (unique assignment per chore+week, weight range check).
- [ ] Create and apply migrations.
- **Done when:** fixtures can be loaded and queried via the Django shell.

## 3. Balancing algorithm (service + tests)
- [ ] Implement weekly generation: equal target load =
      total chore points ÷ member count.
- [ ] Add repeat discouragement using the previous week's assignments
      (streak tracking; only repeat if needed to hit the target).
- [ ] Unit-test the algorithm (even loads, odd loads, repeats discouraged).
- **Done when:** algorithm tests pass with no manual verification needed.

## 4. Views & URLs
- [ ] Pages: members, chores, weekly assignment (generate/regenerate),
      checklist to mark completions.
- [ ] Wire up URLs and simple Django templates.
- **Done when:** each page is reachable and the checklist POST updates
      `completed`.

## 5. Polish & docs
- [ ] Base CSS so pages are readable.
- [ ] `manage.py test` passes; `manage.py check --deploy` has no surprises.
- [ ] Update `README.md` with run instructions.
- **Done when:** a fresh clone can set up and run the app end-to-end.