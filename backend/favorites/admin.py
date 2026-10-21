# backend/favorites/admin.py

"""
Favorites administration — the favorites in the Django admin site
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Register the favorites in the administration interface: a list searchable
by the candidate and by the offer, one page per favorite. Contains no
business logic.
"""

from django.contrib import admin

from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Favorites: list, search, one page per favorite."""

    list_display = ("id", "email", "offer", "company", "created_at")
    list_display_links = ("id", "email")
    search_fields = (
        "candidate__user__email",
        "candidate__user__first_name",
        "candidate__user__last_name",
        "offer__title",
        "offer__employer__company_name",
    )
    ordering = ("-created_at",)
    # The candidate and the offer are chosen by typing part of their address
    # or title, not in a list of every row (searches done by
    # CandidateProfileAdmin and JobOfferAdmin)
    autocomplete_fields = ("candidate", "offer")
    readonly_fields = ("created_at",)
    # Load the candidate's account and the offer's employer with each
    # favorite of the list, in a single query: the columns read them
    list_select_related = ("candidate__user", "offer__employer")

    @admin.display(ordering="candidate__user__email", description="candidate")
    def email(self, favorite):
        """Address of the candidate, as a column of the list."""
        return favorite.candidate.user.email

    @admin.display(ordering="offer__employer__company_name", description="company")
    def company(self, favorite):
        """Name of the company behind the offer, as a column of the list."""
        return favorite.offer.employer.company_name
