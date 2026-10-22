# backend/appointments/admin.py

"""
Appointments administration — the appointments in the Django admin site
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Show the appointments in the administration interface, read only: in line
on the page of their application, and as a list filtered by state and
searchable by the participants and the offer. Nobody proposes or answers
from the admin: that is the work of the participants, through the API.
Contains no business logic.

The line of appointments is added to the page of an application from
here, as the messages are: the applications know nothing of the
appointments, which depend on them.
"""

from django.contrib import admin

from applications.admin import JobApplicationAdmin

from .models import Appointment

# Every field, shown and never changed
FIELDS = (
    "starts_at",
    "duration",
    "place",
    "note",
    "status",
    "response",
    "answered_at",
    "created_at",
    "seen_at",
)


class AppointmentInline(admin.TabularInline):
    """The appointments of an application, read only."""

    model = Appointment
    extra = 0
    can_delete = False
    fields = FIELDS
    readonly_fields = FIELDS

    def has_add_permission(self, request, obj=None):
        """No appointment proposed from the admin."""
        return False


# The page of an application shows its appointments after its conversation
JobApplicationAdmin.inlines = (*JobApplicationAdmin.inlines, AppointmentInline)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Appointments: list, filters, search, one page each, all read only."""

    list_display = ("id", "application", "starts_at", "duration", "status", "answered_at")
    list_filter = ("status",)
    search_fields = (
        "application__offer__title",
        "application__offer__employer__user__email",
        "application__candidate__user__email",
        "place",
    )
    ordering = ("-starts_at",)
    readonly_fields = ("application", *FIELDS)
    # Load the offer with each appointment of the list, in a single query
    list_select_related = ("application__offer",)

    def has_add_permission(self, request):
        """No appointment proposed from the admin."""
        return False
