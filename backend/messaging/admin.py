# backend/messaging/admin.py

"""
Messaging administration — the messages in the Django admin site
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Show the messages in the administration interface, read only: in line on
the page of their application, and as a list searchable by the author and
by the offer. Nobody writes a message from the admin: a message is
written by a participant, through the API. Contains no business logic.

The line of messages is added to the page of an application from here,
not from applications/admin.py: the applications know nothing of the
messaging, which depends on them.
"""

from django.contrib import admin

from applications.admin import JobApplicationAdmin

from .models import Message


class MessageInline(admin.TabularInline):
    """The conversation of an application, read only."""

    model = Message
    extra = 0
    can_delete = False
    fields = ("author", "body", "sent_at", "read_at")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        """No message written from the admin."""
        return False


# The page of an application shows its conversation after its history and
# its attachments
JobApplicationAdmin.inlines = (*JobApplicationAdmin.inlines, MessageInline)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Messages: list, search, one page per message, all read only."""

    list_display = ("id", "application", "author", "sent_at", "read_at")
    search_fields = (
        "author__email",
        "application__offer__title",
        "application__candidate__user__email",
        "body",
    )
    ordering = ("-sent_at",)
    readonly_fields = ("application", "author", "body", "sent_at", "read_at")
    # Load the author and the offer with each message of the list, in a
    # single query: the columns read them
    list_select_related = ("author", "application__offer")

    def has_add_permission(self, request):
        """No message written from the admin."""
        return False
