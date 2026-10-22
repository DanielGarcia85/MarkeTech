# backend/applications/admin.py

"""
Applications administration — job applications in the Django admin site
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Register the job applications in the administration interface: a list
filtered by state, searchable by the candidate and by the offer, one page
per application with its history and its attachments in line. Contains no
business logic: a status changed here is recorded in the history by the
model, like one changed by the API.
"""

from django.contrib import admin

from .models import Attachment, JobApplication, StatusChange


class StatusChangeInline(admin.TabularInline):
    """History of an application, read only: it is written by the model."""

    model = StatusChange
    extra = 0
    can_delete = False
    readonly_fields = ("status", "changed_at", "seen_at")

    def has_add_permission(self, request, obj=None):
        """No row added by hand: a change of status adds its own."""
        return False


class AttachmentInline(admin.TabularInline):
    """Documents joined to an application, listed on its page."""

    model = Attachment
    # No empty row offered by default: an attachment is added on purpose
    extra = 0


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """Job applications: list, filters, search, one page per application."""

    list_display = ("id", "email", "offer", "company", "status", "created_at")
    list_display_links = ("id", "email")
    list_filter = ("status",)
    search_fields = (
        "candidate__user__email",
        "candidate__user__first_name",
        "candidate__user__last_name",
        "offer__title",
        "offer__employer__company_name",
    )
    ordering = ("-created_at",)
    # The offer and the candidate are chosen by typing part of their title,
    # company or address, not in a list of every row (searches done by
    # JobOfferAdmin and CandidateProfileAdmin)
    autocomplete_fields = ("offer", "candidate")
    readonly_fields = ("created_at", "updated_at")
    # Load the candidate's account and the offer's employer with each
    # application of the list, in a single query: the columns read them
    list_select_related = ("candidate__user", "offer__employer")
    fieldsets = (
        (None, {"fields": ("offer", "candidate")}),
        ("Files", {"fields": ("cv", "cover_letter")}),
        ("State", {"fields": ("status", "created_at", "updated_at")}),
    )
    inlines = (StatusChangeInline, AttachmentInline)

    @admin.display(ordering="candidate__user__email", description="candidate")
    def email(self, application):
        """Address of the candidate, as a column of the list."""
        return application.candidate.user.email

    @admin.display(ordering="offer__employer__company_name", description="company")
    def company(self, application):
        """Name of the company behind the offer, as a column of the list."""
        return application.offer.employer.company_name
