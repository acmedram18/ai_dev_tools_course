# ChoreBalancer — Plan

## Goal

A local, single-user Django web app for managing shared household chores with
auto-balancing assignment. Chores are auto-assigned each week so each member's
total effort load lands as close to an equal target as possible, while
discouraging the same person from getting the same chore in consecutive weeks.

## Scope (from homework brainstorm)

### Core features
1. **Members & chores management** — add household members and chores, each
   with an effort weight (1–5 points).
2. **Auto-balancing assignment** — each week the app assigns chores so every
   member's total weight per week lands as close to the equal target as
   possible.
3. **Repeat discouragement** — avoids giving the same person the same chore in
   consecutive weeks.
4. **Weekly checklist** — mark assignments as completed for the week.

### Data model (3 models)

| Model       | Fields                                  |
|-------------|-----------------------------------------|
| `Member`    | name                                    |
| `Chore`     | name, weight (1–5 effort points)        |
| `Assignment`| chore, member, week, completed (bool)   |

### The balancing algorithm
- **Weekly target load** = total points of all chores ÷ number of members. Each
  member's target is that same number (or as equal as possible).
- Each week, active chores get assigned so each member's **total load for the
  week** lands closest to target.
- **Discourage repeats**: the streak of consecutive weeks a member has had a
  chore is tracked; the algorithm avoids repeating, and only resorts to a repeat
  if needed to hit the target.

### Views / pages
- Members
- Chores
- Weekly assignment view (auto-generate / regenerate this week)
- Checklist to mark chores completed for the week

### Explicitly out of scope
- Real user accounts / login
- Multi-household
- Prior-week history weighting (beyond repeat rule)
- Notifications / reminders

## Open assumptions (to confirm before building)
1. **Balance model detail**: each member's "load" is compared by total *weight*
   of assigned chores, equalized per week.
2. **Chores scope per week**: every (active) chore gets assigned every week vs.
   some chores being less frequent than weekly.

## Tech stack
- Python 3.12 (managed via uv)
- Django 6.1 (incl. Django templates for pages)
- SQLite (local development)
- Dependency/virtualenv management: uv

## Build steps (proposed)
1. Scaffold Django project + `chores` app.
2. Define models (`Member`, `Chore`, `Assignment`) + migrations.
3. Implement the balancing algorithm (service module + tests).
4. Build views: members, chores, weekly assignment, checklist.
5. Basic templates and styling.
6. Write tests; run Django's checks and test suite.
7. Document `README.md` setup/run steps.

## Definition of done
- Members, chores, and weekly assignments can be created and viewed in the UI.
- Weekly generation assigns chores toward an equal target load without repeating
  the same chore to the same person in consecutive weeks (when possible).
- Assignments can be marked complete via the checklist.
- Tests pass (`python manage.py test`).
