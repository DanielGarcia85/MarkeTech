# backend/appointments/urls.py

"""
Appointments URL table — the routes of the appointments API
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Map the routes of the appointments API to their views, written out one by
one: the appointments of an application hang under it, which a router of
DRF does not nest. Included by config/urls.py under the prefix api/, after
the messaging. Contains no logic.
"""

from django.urls import path

from .views import (
    AnswerView,
    ApplicationAppointmentsView,
    CalendarView,
    CancelView,
    MyAppointmentsView,
    UnseenView,
)

urlpatterns = [
    path(
        "applications/<int:pk>/appointments/",
        ApplicationAppointmentsView.as_view(),
        name="application-appointments",
    ),
    path("appointments/", MyAppointmentsView.as_view(), name="appointment-list"),
    path("appointments/unseen/", UnseenView.as_view(), name="unseen-appointments"),
    path("appointments/<int:pk>/answer/", AnswerView.as_view(), name="appointment-answer"),
    path("appointments/<int:pk>/cancel/", CancelView.as_view(), name="appointment-cancel"),
    path("appointments/<int:pk>/calendar/", CalendarView.as_view(), name="appointment-calendar"),
]
