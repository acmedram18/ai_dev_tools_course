from datetime import timedelta

from .models import Assignment


def monday_of(day):
    """Return the Monday of the week containing ``day``."""
    return day - timedelta(days=day.weekday())


def _repeat_streaks(members, chores, week_start, previous):
    """Map {(member_id, chore_id): streak} for consecutive weeks ending the week
    before ``week_start``."""
    present = {(a.member_id, a.chore_id, a.week_start) for a in previous}
    streaks = {}
    for member in members:
        for chore in chores:
            streak = 0
            current = week_start - timedelta(days=7)
            while (member.id, chore.id, current) in present:
                streak += 1
                current -= timedelta(days=7)
            if streak:
                streaks[(member.id, chore.id)] = streak
    return streaks


def _assign(week_start, members, chores, streaks):
    """Greedy longest-processing-time assignment: heaviest chores first, each to
    the least-loaded member. Repeats (streak >= 1) are avoided unless every
    member would repeat."""
    loads = {member.id: 0 for member in members}
    assignments = []
    for chore in sorted(chores, key=lambda c: c.weight, reverse=True):
        non_repeaters = [
            m for m in members if streaks.get((m.id, chore.id), 0) < 1
        ]
        pool = non_repeaters or members
        member = min(pool, key=lambda m: (loads[m.id], m.id))
        loads[member.id] += chore.weight
        assignments.append(
            Assignment(chore=chore, member=member, week_start=week_start)
        )
    return assignments


def generate_assignments(week_start, *, members=None, chores=None, previous=()):
    """Generate unsaved Assignments for ``week_start``.

    ``previous`` may be an Assignment queryset/list; it is used only to compute
    repeat streaks. When ``members``/``chores`` are omitted they default to all
    members / active chores.
    """
    from .models import Chore, Member

    members = list(members) if members is not None else list(Member.objects.all())
    chores = (
        list(chores)
        if chores is not None
        else list(Chore.objects.filter(is_active=True))
    )
    if not members or not chores:
        return []

    if previous is None:
        previous = Assignment.objects.filter(week_start__lt=week_start)
    previous = list(previous)

    streaks = _repeat_streaks(members, chores, week_start, previous)
    return _assign(week_start, members, chores, streaks)