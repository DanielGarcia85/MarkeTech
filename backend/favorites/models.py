# backend/favorites/models.py

"""
Favorite model — an offer a candidate put aside
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Define a favorite: which candidate put which offer aside, and when. A
favorite exists or does not: no state, no history. It belongs to one
candidate profile and to one offer, and goes away with either; it stays
when the offer is closed, until the candidate removes it (decision of
21.10.2026).

What is not here
────────────────
The rules of the API (who may read or change what): they live in the views
and serializers. The "favorite" flag of an offer, read by the pages to draw
the heart, is computed by the offers API from this table.
"""

from django.db import models

from offers.models import JobOffer
from profiles.models import CandidateProfile


class Favorite(models.Model):
    """One offer put aside by one candidate."""

    # Deleted with the profile of the candidate, and with the offer. From
    # the profile: profile.favorites; from the offer: offer.favorites
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    offer = models.ForeignKey(
        JobOffer,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Newest first, wherever the favorites are listed
        ordering = ["-created_at"]
        constraints = [
            # An offer is put aside once by a candidate, refused by the
            # database itself
            models.UniqueConstraint(
                fields=["candidate", "offer"],
                name="one_favorite_per_candidate_and_offer",
                violation_error_message="This offer is already in your favourites.",
            ),
        ]

    def __str__(self):
        return f"Favorite {self.pk}: {self.offer}"
