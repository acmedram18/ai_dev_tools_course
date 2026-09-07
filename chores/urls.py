from django.urls import path

from . import views

app_name = "chores"

urlpatterns = [
    path("", views.home, name="home"),
    path("members/", views.members_view, name="members"),
    path("chores/", views.chores_view, name="chores"),
    path("week/", views.week_view, name="week"),
    path(
        "week/<int:year>/<int:month>/<int:day>/",
        views.week_view,
        name="week-date",
    ),
    path(
        "week/<int:year>/<int:month>/<int:day>/generate/",
        views.generate_week,
        name="week-generate",
    ),
    path(
        "week/<int:year>/<int:month>/<int:day>/complete/",
        views.complete_week,
        name="week-complete",
    ),
]