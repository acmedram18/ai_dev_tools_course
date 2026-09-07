from django.contrib import admin

from .models import Assignment, Chore, Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "weight", "is_active")
    list_filter = ("is_active",)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "chore", "member", "week_start", "completed")
    list_filter = ("week_start", "completed")