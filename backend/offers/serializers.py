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
and close routes, the dates are set by the model.
"""

from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from .models import JobOffer


class JobOfferSerializer(CountryFieldMixin, serializers.ModelSerializer):
    """A job offer, for the public list as for its employer."""

    company = serializers.SerializerMethodField()

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
        ]
        read_only_fields = ["status", "published_at", "created_at", "updated_at"]

    def get_company(self, offer):
        """The company as the profile of the employer says it today."""
        employer = offer.employer
        return {
            "name": employer.company_name,
            "logo": employer.logo.url if employer.logo else None,
        }

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
