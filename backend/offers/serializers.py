# backend/offers/serializers.py

"""
Offer serializer — the JSON shape of a job offer
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Turn a job offer into JSON for the API, and read back what an employer
sends, with the checks of the model (lengths, bounds, choices) and the ones
that need two fields (the ranges). Contains no view: views.py decides who
may do what, and changes the status.

What the JSON looks like
────────────────────────
Every field of the model as it is, the country as its two-letter code, the
choices as their stored values (draft, permanent, hybrid...: the frontend
has the translated texts), plus "company": the name and the logo URL read on
the profile of the employer at the time of the answer, never copied. The
status and the dates are read only: the status moves through the publish
and close routes, the dates are set by the model. "mine": whether the
offer belongs to the user asking, so that the pages know what to offer
(editing, the applications) without comparing names. "favorite": whether
the candidate asking put the offer aside (the heart), computed by the view
for a candidate, false for anyone else. For the employer of the offer
only, "applications_count" and "favorites_count": how many candidates
applied, how many put it aside (the public does not need them, and an
offer does not say how many compete for it).
"""

from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from .models import JobOffer


class JobOfferSerializer(CountryFieldMixin, serializers.ModelSerializer):
    """A job offer, for the public list as for its employer."""

    company = serializers.SerializerMethodField()
    mine = serializers.SerializerMethodField()
    favorite = serializers.SerializerMethodField()

    class Meta:
        model = JobOffer
        fields = [
            "id",
            "title",
            "description",
            "city",
            "country",
            "remote",
            "contract",
            "workload_min",
            "workload_max",
            "salary_min",
            "salary_max",
            "salary_period",
            "currency",
            "experience_years",
            "status",
            "published_at",
            "created_at",
            "updated_at",
            "company",
            "mine",
            "favorite",
        ]
        read_only_fields = ["status", "published_at", "created_at", "updated_at"]

    def get_company(self, offer):
        """The company as the profile of the employer says it today."""
        employer = offer.employer
        return {
            "name": employer.company_name,
            "logo": employer.logo.url if employer.logo else None,
        }

    def get_mine(self, offer):
        """Whether the user asking is the employer of the offer; false for
        a visitor, a candidate, another employer, or without a request."""
        request = self.context.get("request")
        return bool(request) and offer.employer.user_id == request.user.pk

    def get_favorite(self, offer):
        """Whether the candidate asking put the offer aside: annotated by the
        view for a candidate (favorites/models.py), absent otherwise."""
        return bool(getattr(offer, "favorite", False))

    def validate(self, data):
        """The checks that need more than one field: a range is not reversed."""
        # The value after the change: what is sent, else what is stored
        def value(field):
            return data.get(field, getattr(self.instance, field, None))

        errors = {}
        for low, high in (("salary_min", "salary_max"), ("workload_min", "workload_max")):
            if value(low) and value(high) and value(low) > value(high):
                errors[high] = "The maximum must be at least the minimum."
        if errors:
            raise serializers.ValidationError(errors)
        return data


class MyOfferSerializer(JobOfferSerializer):
    """A job offer as its employer sees it: the same, with the numbers of
    applications received and of candidates who put it aside. Never given
    for somebody else's offer."""

    applications_count = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()

    class Meta(JobOfferSerializer.Meta):
        fields = JobOfferSerializer.Meta.fields + ["applications_count", "favorites_count"]

    def get_applications_count(self, offer):
        """Counted by the query of the list when it did (mine), else now."""
        count = getattr(offer, "applications_count", None)
        return offer.applications.count() if count is None else count

    def get_favorites_count(self, offer):
        count = getattr(offer, "favorites_count", None)
        return offer.favorites.count() if count is None else count
