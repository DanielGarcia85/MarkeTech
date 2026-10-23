# backend/reviews/admin.py

"""
Reviews administration — the reviews in the Django admin site
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Show the reviews in the administration interface: a list searchable by
the author and the comment, one page per review, read only. The
administrator may delete a review (the terms of use allow it to remove a
content); nobody writes one from the admin. Contains no business logic.
"""

from django.contrib import admin

from .models import CRITERIA, Review

# Every field, shown and never changed
FIELDS = ("user", "rating", *CRITERIA, "comment", "created_at", "updated_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Reviews: list, search, one page each, read only, deletable."""

    list_display = ("id", "email", "rating", "created_at", "updated_at")
    list_display_links = ("id", "email")
    list_filter = ("rating",)
    search_fields = ("user__email", "user__first_name", "user__last_name", "comment")
    ordering = ("-created_at",)
    fields = FIELDS
    readonly_fields = FIELDS
    # Load the author with each review of the list, in a single query
    list_select_related = ("user",)

    @admin.display(ordering="user__email", description="author")
    def email(self, review):
        """Address of the author, as a column of the list."""
        return review.user.email

    def has_add_permission(self, request):
        """No review written from the admin."""
        return False
