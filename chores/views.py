from datetime import date

from django import forms
from django.shortcuts import redirect, render

from .balancer import generate_assignments, monday_of
from .models import Assignment, Chore, Member


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["name"]


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ["name", "weight"]


def home(request):
    week_start = monday_of(date.today())
    context = {
        "week_start": week_start,
        "member_count": Member.objects.count(),
        "chore_count": Chore.objects.filter(is_active=True).count(),
    }
    return render(request, "chores/home.html", context)


def members_view(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("chores:members")
    else:
        form = MemberForm()
    context = {"members": Member.objects.all(), "form": form}
    return render(request, "chores/members.html", context)


def chores_view(request):
    if request.method == "POST":
        form = ChoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("chores:chores")
    else:
        form = ChoreForm()
    context = {"chores": Chore.objects.all(), "form": form}
    return render(request, "chores/chores.html", context)


def _resolve_week(year, month, day):
    if year is None:
        return monday_of(date.today())
    return monday_of(date(year, month, day))


def week_view(request, year=None, month=None, day=None):
    week_start = _resolve_week(year, month, day)
    assignments = (
        Assignment.objects.filter(week_start=week_start)
        .select_related("chore", "member")
        .order_by("-chore__weight")
    )
    context = {
        "week_start": week_start,
        "assignments": assignments,
        "generated": assignments.exists(),
    }
    return render(request, "chores/week.html", context)


def generate_week(request, year, month, day):
    week_start = _resolve_week(year, month, day)
    if request.method == "POST":
        Assignment.objects.filter(week_start=week_start).delete()
        Assignment.objects.bulk_create(generate_assignments(week_start))
    return redirect("chores:week-date", year=week_start.year,
                    month=week_start.month, day=week_start.day)


def complete_week(request, year, month, day):
    week_start = _resolve_week(year, month, day)
    if request.method == "POST":
        completed_ids = {int(pk) for pk in request.POST.getlist("completed")}
        for assignment in Assignment.objects.filter(week_start=week_start):
            done = assignment.id in completed_ids
            if assignment.completed != done:
                assignment.completed = done
                assignment.save(update_fields=["completed"])
    return redirect("chores:week-date", year=week_start.year,
                    month=week_start.month, day=week_start.day)