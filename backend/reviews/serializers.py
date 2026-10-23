# backend/reviews/serializers.py

"""
Reviews serializers — the JSON shape of the reviews
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Turn a review into JSON for the pages: the five scores, the comment, when
it was written and last changed, whether it is the review of the user
asking, and its author as the public sees them: the first name and the
initial of the last name, the role, and the company for an employer
(decisions of 23.10.2026). Never the e-mail address, never the full last
name. Check what an author sends: five scores from 1 to 5 and a comment.
Who may write is decided by the views.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import CRITERIA, HIGHEST, LOWEST, MAX_LENGTH, Review

# One sentence for every way a score can be wrong
SCORE = _("Give a score from 1 to 5.")


def public_name(user):
    """"Léa M.": the first name and the initial of the last name; the first
    name alone without a last name; None without a first name (the page
    then says "A user")."""
    first = user.first_name.strip()
    if not first:
        return None
    last = user.last_name.strip()
    return f"{first} {last[0].upper()}." if last else first


def company_of(user):
    """The name of the company of an employer, None if it has none yet."""
    try:
        return user.employer_profile.company_name or None
    except ObjectDoesNotExist:
        # An employer made in the admin site, without a profile
        return None


class ReviewSerializer(serializers.ModelSerializer):
    """A review as the pages show it. Reads the author and the profile of
    an employer: the views load them with the reviews (select_related)."""

    author = serializers.SerializerMethodField()
    mine = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            *CRITERIA,
            "comment",
            "created_at",
            "updated_at",
            "author",
            "mine",
        ]
        read_only_fields = fields

    def get_author(self, review):
        user = review.user
        return {
            "name": public_name(user),
            "role": user.role,
            "company": company_of(user) if user.role == "employer" else None,
        }

    def get_mine(self, review):
        """The review of the user asking: the page offers to change it."""
        request = self.context.get("request")
        return bool(request and review.user_id == request.user.pk)


def score_field():
    """A whole score from 1 to 5, required."""
    return serializers.IntegerField(
        min_value=LOWEST,
        max_value=HIGHEST,
        error_messages={
            "required": SCORE,
            "null": SCORE,
            "invalid": SCORE,
            "min_value": SCORE,
            "max_value": SCORE,
        },
    )


class WriteSerializer(serializers.Serializer):
    """What an author sends, to write or rewrite their review: the five
    scores and a comment."""

    rating = score_field()
    ease_of_use = score_field()
    offers_and_applications = score_field()
    messaging = score_field()
    appointments = score_field()
    comment = serializers.CharField(
        max_length=MAX_LENGTH,
        trim_whitespace=True,
        error_messages={
            "blank": _("Write a few words about the platform."),
            "required": _("Write a few words about the platform."),
            "max_length": _("A review has at most {max_length} characters."),
        },
    )
