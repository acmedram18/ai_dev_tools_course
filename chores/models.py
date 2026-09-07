from django.db import models


class Member(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Chore(models.Model):
    name = models.CharField(max_length=100, unique=True)
    weight = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(weight__gte=1, weight__lte=5),
                name="weight_between_1_and_5",
            ),
        ]

    def __str__(self):
        return self.name


class Assignment(models.Model):
    chore = models.ForeignKey(
        Chore, on_delete=models.CASCADE, related_name="assignments"
    )
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="assignments"
    )
    week_start = models.DateField(help_text="Monday of the assignment week")
    completed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["chore", "week_start"],
                name="one_assignment_per_chore_per_week",
            ),
        ]

    def __str__(self):
        return f"{self.chore} -> {self.member} ({self.week_start})"