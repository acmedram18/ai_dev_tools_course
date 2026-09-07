from datetime import date, timedelta

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .balancer import generate_assignments, monday_of
from .models import Assignment, Chore, Member


def loads_of(assignments):
    loads = {}
    for a in assignments:
        loads[a.member] = loads.get(a.member, 0) + a.chore.weight
    return loads


def week_url(week):
    return reverse(
        "chores:week-date",
        args=[week.year, week.month, week.day],
    )


def generate_url(week):
    return reverse(
        "chores:week-generate",
        args=[week.year, week.month, week.day],
    )


def complete_url(week):
    return reverse(
        "chores:week-complete",
        args=[week.year, week.month, week.day],
    )


class ModelTests(TestCase):
    def test_member_str(self):
        self.assertEqual(str(Member.objects.create(name="Ana")), "Ana")

    def test_chore_str(self):
        self.assertEqual(str(Chore.objects.create(name="Dishes", weight=2)), "Dishes")

    def test_assignment_str(self):
        member = Member.objects.create(name="Ana")
        chore = Chore.objects.create(name="Dishes", weight=2)
        week = monday_of(date(2026, 9, 7))
        assignment = Assignment.objects.create(
            chore=chore, member=member, week_start=week
        )
        self.assertEqual(str(assignment), "Dishes -> Ana (2026-09-07)")

    def test_weight_boundaries_accepted(self):
        Chore.objects.create(name="light", weight=1)
        Chore.objects.create(name="heavy", weight=5)
        self.assertEqual(Chore.objects.count(), 2)

    def test_weight_zero_rejected(self):
        with self.assertRaises(Exception):
            Chore.objects.create(name="invalid", weight=0)

    def test_weight_six_rejected(self):
        with self.assertRaises(Exception):
            Chore.objects.create(name="invalid", weight=6)

    def test_is_active_defaults_true(self):
        chore = Chore.objects.create(name="Dishes", weight=1)
        self.assertTrue(chore.is_active)

    def test_completed_defaults_false(self):
        member = Member.objects.create(name="Ana")
        chore = Chore.objects.create(name="Dishes", weight=1)
        assignment = Assignment.objects.create(
            chore=chore, member=member, week_start=monday_of(date(2026, 9, 7))
        )
        self.assertFalse(assignment.completed)

    def test_duplicate_member_name_rejected(self):
        Member.objects.create(name="Ana")
        with self.assertRaises(Exception):
            Member.objects.create(name="Ana")

    def test_duplicate_chore_name_rejected(self):
        Chore.objects.create(name="Dishes", weight=1)
        with self.assertRaises(Exception):
            Chore.objects.create(name="Dishes", weight=2)

    def test_duplicate_assignment_rejected(self):
        member = Member.objects.create(name="Ana")
        chore = Chore.objects.create(name="Dishes", weight=1)
        week = monday_of(date(2026, 9, 7))
        Assignment.objects.create(chore=chore, member=member, week_start=week)
        with self.assertRaises(Exception):
            Assignment.objects.create(
                chore=chore, member=member, week_start=week
            )

    def test_member_delete_cascades(self):
        member = Member.objects.create(name="Ana")
        chore = Chore.objects.create(name="Dishes", weight=1)
        Assignment.objects.create(
            chore=chore, member=member, week_start=monday_of(date(2026, 9, 7))
        )
        member.delete()
        self.assertEqual(Assignment.objects.count(), 0)


class MondayOfTests(TestCase):
    def test_midweek_returns_that_monday(self):
        self.assertEqual(monday_of(date(2026, 9, 9)), date(2026, 9, 7))

    def test_monday_returns_itself(self):
        self.assertEqual(monday_of(date(2026, 9, 7)), date(2026, 9, 7))

    def test_sunday_returns_previous_monday(self):
        self.assertEqual(monday_of(date(2026, 9, 6)), date(2026, 8, 31))


class BalancerTests(TestCase):
    def setUp(self):
        self.ana = Member.objects.create(name="Ana")
        self.bruno = Member.objects.create(name="Bruno")
        self.carla = Member.objects.create(name="Carla")

    def chore(self, name, weight, active=True):
        return Chore.objects.create(name=name, weight=weight, is_active=active)

    @staticmethod
    def week(n):
        return monday_of(date(2026, 9, 7)) + timedelta(days=7 * n)

    def test_even_load_two_members(self):
        dishes = self.chore("Dishes", 3)
        trash = self.chore("Trash", 2)
        assignments = generate_assignments(
            self.week(1), members=[self.ana, self.bruno], chores=[dishes, trash]
        )
        loads = sorted(loads_of(assignments).values())
        self.assertEqual(len(assignments), 2)
        self.assertLessEqual(loads[-1] - loads[0], 1)
        self.assertEqual(sum(loads), 5)

    def test_odd_members_equal_target(self):
        chores = [
            self.chore(f"chore-{i}", w)
            for i, w in enumerate([5, 5, 3, 3, 1, 1])
        ]
        assignments = generate_assignments(
            self.week(1),
            members=[self.ana, self.bruno, self.carla],
            chores=chores,
        )
        self.assertEqual(set(loads_of(assignments).values()), {6})

    def test_near_target_when_total_not_divisible(self):
        chores = [
            self.chore(f"chore-{i}", w)
            for i, w in enumerate([5, 5, 3, 3, 1, 1, 1])
        ]
        assignments = generate_assignments(
            self.week(1),
            members=[self.ana, self.bruno, self.carla],
            chores=chores,
        )
        loads = sorted(loads_of(assignments).values())
        self.assertEqual(len(assignments), 7)
        self.assertEqual(sum(loads), 19)
        self.assertLessEqual(loads[-1] - loads[0], 1)

    def test_unbalanced_weights_stay_close(self):
        chores = [
            self.chore(f"chore-{i}", w)
            for i, w in enumerate([5, 4, 4, 3, 2, 1, 1])
        ]
        assignments = generate_assignments(
            self.week(1),
            members=[self.ana, self.bruno, self.carla],
            chores=chores,
        )
        loads = list(loads_of(assignments).values())
        self.assertEqual(sum(loads), 20)
        self.assertEqual(max(loads) - min(loads), 1)

    def test_deterministic_tie_break(self):
        c1 = self.chore("c1", 2)
        c2 = self.chore("c2", 2)
        members = [self.ana, self.bruno]
        first = generate_assignments(self.week(1), members=members, chores=[c1, c2])
        second = generate_assignments(self.week(1), members=members, chores=[c1, c2])
        self.assertEqual(
            {a.chore: a.member for a in first},
            {a.chore: a.member for a in second},
        )

    def test_repeats_discouraged(self):
        c1 = self.chore("c1", 2)
        c2 = self.chore("c2", 2)
        Assignment.objects.create(chore=c1, member=self.ana, week_start=self.week(0))
        Assignment.objects.create(chore=c2, member=self.bruno, week_start=self.week(0))
        assignments = generate_assignments(
            self.week(1),
            members=[self.ana, self.bruno],
            chores=[c1, c2],
            previous=Assignment.objects.all(),
        )
        by_chore = {a.chore: a.member for a in assignments}
        self.assertEqual(by_chore[c1], self.bruno)
        self.assertEqual(by_chore[c2], self.ana)

    def test_multi_week_streak_no_repeat(self):
        c1 = self.chore("c1", 2)
        c2 = self.chore("c2", 2)
        for prev_week in (self.week(0), self.week(1)):
            Assignment.objects.create(
                chore=c1, member=self.ana, week_start=prev_week
            )
            Assignment.objects.create(
                chore=c2, member=self.bruno, week_start=prev_week
            )
        assignments = generate_assignments(
            self.week(2),
            members=[self.ana, self.bruno],
            chores=[c1, c2],
            previous=Assignment.objects.all(),
        )
        by_chore = {a.chore: a.member for a in assignments}
        self.assertEqual(by_chore[c1], self.bruno)
        self.assertEqual(by_chore[c2], self.ana)

    def test_gap_week_resets_streak(self):
        c1 = self.chore("c1", 2)
        Assignment.objects.create(chore=c1, member=self.ana, week_start=self.week(0))
        assignments = generate_assignments(
            self.week(2),  # week(1) has no assignments at all
            members=[self.ana, self.bruno],
            chores=[c1],
            previous=Assignment.objects.all(),
        )
        self.assertEqual(assignments[0].member, self.ana)

    def test_repeat_forced_with_single_member(self):
        c1 = self.chore("c1", 2)
        c2 = self.chore("c2", 2)
        assignments = generate_assignments(
            self.week(1), members=[self.ana], chores=[c1, c2]
        )
        self.assertEqual(len(assignments), 2)
        self.assertTrue(all(a.member == self.ana for a in assignments))

    def test_previous_none_uses_database_history(self):
        c1 = self.chore("c1", 2)
        c2 = self.chore("c2", 2)
        Assignment.objects.create(chore=c1, member=self.ana, week_start=self.week(0))
        Assignment.objects.create(chore=c2, member=self.bruno, week_start=self.week(0))
        assignments = generate_assignments(
            self.week(1),
            members=[self.ana, self.bruno],
            chores=[c1, c2],
            previous=None,
        )
        by_chore = {a.chore: a.member for a in assignments}
        self.assertEqual(by_chore[c1], self.bruno)
        self.assertEqual(by_chore[c2], self.ana)

    def test_defaults_to_active_chores_only(self):
        active1 = self.chore("active1", 1)
        self.chore("inactive", 3, active=False)
        assignments = generate_assignments(self.week(1), members=[self.ana])
        self.assertEqual([a.chore for a in assignments], [active1])

    def test_no_members_or_chores_returns_empty(self):
        self.assertEqual(generate_assignments(self.week(1), members=[]), [])
        self.assertEqual(generate_assignments(self.week(1), chores=[]), [])


class ViewTests(TestCase):
    def setUp(self):
        self.ana = Member.objects.create(name="Ana")
        self.bruno = Member.objects.create(name="Bruno")
        Chore.objects.create(name="Dishes", weight=3)
        Chore.objects.create(name="Trash", weight=2)
        self.week = monday_of(date(2026, 9, 7))

    def test_pages_reachable(self):
        for name in ("chores:home", "chores:members", "chores:chores", "chores:week"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.assertEqual(self.client.get(week_url(self.week)).status_code, 200)

    def test_home_shows_counts(self):
        response = self.client.get(reverse("chores:home"))
        self.assertContains(response, "2 members")
        self.assertContains(response, "2 active chores")

    def test_add_member(self):
        response = self.client.post(reverse("chores:members"), {"name": "Carla"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Member.objects.filter(name="Carla").exists())

    def test_duplicate_member_shows_error(self):
        response = self.client.post(reverse("chores:members"), {"name": "Ana"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Member.objects.count(), 2)

    def test_add_chore(self):
        response = self.client.post(
            reverse("chores:chores"), {"name": "Bathroom", "weight": "5"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Chore.objects.filter(name="Bathroom").exists())

    def test_duplicate_chore_shows_error(self):
        response = self.client.post(
            reverse("chores:chores"), {"name": "Dishes", "weight": "3"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Chore.objects.count(), 2)

    def test_invalid_weight_zero_shows_error(self):
        response = self.client.post(
            reverse("chores:chores"), {"name": "TooLight", "weight": "0"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Chore.objects.filter(name="TooLight").exists())

    def test_invalid_weight_six_shows_error(self):
        for weight in ("6", "abc"):
            response = self.client.post(
                reverse("chores:chores"), {"name": "TooHeavy", "weight": weight}
            )
            self.assertEqual(response.status_code, 200)
            self.assertFalse(Chore.objects.filter(name="TooHeavy").exists())

    def test_generate_week_creates_assignments(self):
        response = self.client.post(generate_url(self.week))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Assignment.objects.filter(week_start=self.week).count(), 2)

    def test_regenerate_keeps_count_and_resets_completed(self):
        self.client.post(generate_url(self.week))
        assignment = Assignment.objects.filter(week_start=self.week).first()
        self.client.post(complete_url(self.week), {"completed": [str(assignment.id)]})
        assignment.refresh_from_db()
        self.assertTrue(assignment.completed)

        self.client.post(generate_url(self.week))
        assignments = Assignment.objects.filter(week_start=self.week)
        self.assertEqual(assignments.count(), 2)
        self.assertFalse(any(a.completed for a in assignments))

    def test_checklist_updates_completed(self):
        self.client.post(generate_url(self.week))
        assignment = Assignment.objects.filter(week_start=self.week).first()
        other = Assignment.objects.filter(week_start=self.week).exclude(
            pk=assignment.pk
        ).first()
        self.client.post(
            complete_url(self.week), {"completed": [str(assignment.id)]}
        )
        assignment.refresh_from_db()
        other.refresh_from_db()
        self.assertTrue(assignment.completed)
        self.assertFalse(other.completed)

    def test_checklist_uncheck_all(self):
        self.client.post(generate_url(self.week))
        self.client.post(
            complete_url(self.week),
            {"completed": [str(a.id) for a in Assignment.objects.filter(week_start=self.week)]},
        )
        self.assertTrue(
            all(
                a.completed
                for a in Assignment.objects.filter(week_start=self.week)
            )
        )
        self.client.post(complete_url(self.week), {})
        self.assertFalse(
            any(
                a.completed
                for a in Assignment.objects.filter(week_start=self.week)
            )
        )

    def test_get_on_generate_does_not_mutate(self):
        response = self.client.get(generate_url(self.week))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Assignment.objects.count(), 0)

    def test_get_on_complete_does_not_mutate(self):
        self.client.post(generate_url(self.week))
        before = {
            a.id: a.completed for a in Assignment.objects.filter(week_start=self.week)
        }
        response = self.client.get(complete_url(self.week))
        self.assertEqual(response.status_code, 302)
        after = {
            a.id: a.completed for a in Assignment.objects.filter(week_start=self.week)
        }
        self.assertEqual(before, after)

    def test_week_date_normalizes_to_monday(self):
        wednesday = date(2026, 9, 9)
        self.client.post(generate_url(wednesday))
        assignments = Assignment.objects.filter(
            week_start=monday_of(wednesday)
        )
        self.assertEqual(assignments.count(), 2)
        self.assertTrue(
            all(a.week_start == date(2026, 9, 7) for a in assignments)
        )

    def test_week_page_shows_empty_state(self):
        week = self.week + timedelta(days=7)
        response = self.client.get(week_url(week))
        self.assertContains(response, "Generate assignments")
        self.assertContains(response, "No assignments for this week yet")

    def test_week_page_lists_assignments(self):
        self.client.post(generate_url(self.week))
        response = self.client.get(week_url(self.week))
        self.assertContains(response, "Ana")
        self.assertContains(response, "Bruno")
        self.assertContains(response, "Dishes")
        self.assertContains(response, "Trash")
        self.assertContains(response, "Save checklist")


class ActiveChoreViewTests(TestCase):
    def setUp(self):
        Member.objects.create(name="Ana")
        Chore.objects.create(name="Active", weight=2)
        Chore.objects.create(name="Paused", weight=1, is_active=False)
        self.week = monday_of(date(2026, 9, 7))

    def test_generate_ignores_inactive_chores(self):
        self.client.post(generate_url(self.week))
        assignments = Assignment.objects.filter(week_start=self.week)
        self.assertEqual(assignments.count(), 1)
        self.assertEqual(assignments.first().chore.name, "Active")


class FixtureTests(TestCase):
    def test_sample_fixture_loads(self):
        call_command("loaddata", "sample", verbosity=0)
        self.assertEqual(Member.objects.count(), 3)
        self.assertEqual(Chore.objects.count(), 4)
        self.assertEqual(Chore.objects.filter(is_active=True).count(), 3)