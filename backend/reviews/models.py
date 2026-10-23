# backend/reviews/models.py

"""
Review model — what a user thinks of the platform
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Define a review of the platform: its author, an overall rating and four
detailed ones from 1 to 5, a comment, when it was written and last changed
(decisions of 23.10.2026). One review per account, a rule of the database
itself (the one-to-one link): the team deliverable checked it in its view
and answered "created" without saving a second one. Candidates and
employers review; an administrator, who has no role, does not (the API
decides). The review goes with its account.

The four criteria fit both roles and what the site does: how easy it is to
use, the offers and the applications (finding and applying, or publishing
and handling), the messaging, the appointments.

What is not here
────────────────
Who may write (the views), the averages (computed by the API), the name
shown in public (first name and initial, by the serializer).
"""

from django.conf import settings
from django.db import models

# The longest comment accepted
MAX_LENGTH = 1000

# The scores, from 1 to 5
LOWEST, HIGHEST = 1, 5

# The detailed criteria, in the order the pages show them
CRITERIA = ("ease_of_use", "offers_and_applications", "messaging", "appointments")


def score():
    """A score from 1 to 5, required."""
    return models.PositiveSmallIntegerField()


class Review(models.Model):
    """The review of one account."""

    # One review per account, refused twice by the database; from the
    # account: user.review
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review",
    )
    rating = score()
    ease_of_use = score()
    offers_and_applications = score()
    messaging = score()
    appointments = score()
    comment = models.TextField(max_length=MAX_LENGTH)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # The newest first, as the page lists them
        ordering = ["-created_at", "-pk"]
        constraints = [
            # Every score between 1 and 5, refused otherwise by the database
            *(
                models.CheckConstraint(
                    condition=models.Q(**{f"{field}__gte": LOWEST, f"{field}__lte": HIGHEST}),
                    name=f"review_{field}_from_1_to_5",
                    violation_error_message="A score goes from 1 to 5.",
                )
                for field in ("rating", *CRITERIA)
            ),
            # A review says something
            models.CheckConstraint(
                condition=~models.Q(comment=""),
                name="review_comment_not_empty",
                violation_error_message="A review needs a comment.",
            ),
        ]

    def __str__(self):
        return f"Review {self.pk} by user {self.user_id}"
