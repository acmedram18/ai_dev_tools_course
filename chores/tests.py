from datetime import date, timedelta

from django.test import TestCase

from .balancer import generate_assignments, monday_of
from .models import Assignment, Chore, Member


def loads_of(assignments):
    loads = {}
    for a in assignments:
        loads[a.member] = loads.get(a.member, 0) + a.chore.weight
    return loads


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

    def test_monday_of_returns_monday(self):
        day = date(2026, 9, 9)
        monday = monday_of(day)
        self.assertEqual(monday.weekday(), 0)
        self.assertLessEqual(monday, day)
        self.assertLess(day, monday + timedelta(days=7))

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
        loads = loads_of(assignments)
        self.assertEqual(set(loads.values()), {6})

    def test_repeats_discouraged(self):
        c1 = self.chore("c1", 2)
        c2 = self.chore("c2", 2)
        member_list = [self.ana, self.bruno]
        Assignment.objects.create(
            chore=c1, member=self.ana, week_start=self.week(0)
        )
        Assignment.objects.create(
            chore=c2, member=self.bruno, week_start=self.week(0)
        )
        assignments = generate_assignments(
            self.week(1),
            members=member_list,
            chores=[c1, c2],
            previous=Assignment.objects.all(),
        )
        by_chore = {a.chore: a.member for a in assignments}
        self.assertEqual(by_chore[c1], self.bruno)
        self.assertEqual(by_chore[c2], self.ana)

    def test_repeat_forced_with_single_member(self):
        c1 = self.chore("c1", 2)
        c2 = self.chore("c2", 2)
        assignments = generate_assignments(
            self.week(1), members=[self.ana], chores=[c1, c2]
        )
        self.assertEqual(len(assignments), 2)
        self.assertTrue(all(a.member == self.ana for a in assignments))

    def test_defaults_to_active_chores_only(self):
        active1 = self.chore("active1", 1)
        self.chore("inactive", 3, active=False)
        assignments = generate_assignments(self.week(1), members=[self.ana])
        self.assertEqual([a.chore for a in assignments], [active1])

    def test_no_members_returns_empty(self):
        self.assertEqual(generate_assignments(self.week(1), members=[]), [])


class ModelConstraintTests(TestCase):
    def test_weight_out_of_range_rejected(self):
        with self.assertRaises(Exception):
            Chore.objects.create(name="invalid", weight=9)

    def test_duplicate_assignment_rejected(self):
        member = Member.objects.create(name="Ana")
        chore = Chore.objects.create(name="Dishes", weight=1)
        week = monday_of(date(2026, 9, 7))
        Assignment.objects.create(chore=chore, member=member, week_start=week)
        with self.assertRaises(Exception):
            Assignment.objects.create(
                chore=chore, member=member, week_start=week
            )