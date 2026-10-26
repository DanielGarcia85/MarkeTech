# backend/offers/models.py

"""
Job offer model — what an employer publishes
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Define a job offer: its text, its place, its conditions (contract, workload,
remote work, salary, experience), and its state in the life of the offer.
An offer belongs to one employer profile and goes away with it.

What is not here
────────────────
The name and the logo of the company: they are read on the profile of the
employer whenever the offer is shown (the original project copied them into
every offer at creation, and they went stale). Nor the rules of the API
(who may read or change what): they live in the views and serializers.

The states
──────────
draft: being written, seen by its employer only. published: in the public
list, from published_at. closed: withdrawn, kept by its employer as history
and reopenable. Decisions of 20.10.2026.

The offers of a blocked account
───────────────────────────────
An account the administrator blocks (is_active unticked in the admin) takes
its offers out of sight: public() leaves them out, and they come back as
they were when the account is unblocked (decision of 26.10.2026). Nothing
is deleted.
"""

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from django.utils.translation import gettext as _
from django_countries.fields import CountryField

from profiles.models import EmployerProfile


def public_offer():
    """The condition of an offer anyone may see: published, by an account
    that is not blocked. The list, the detail, the applications and the
    favorites all start from it."""
    return Q(status=JobOffer.Status.PUBLISHED, employer__user__is_active=True)


class OfferQuerySet(models.QuerySet):
    """The ways to select offers, on JobOffer.objects."""

    def public(self):
        """The offers anyone may see (public_offer)."""
        return self.filter(public_offer())


class JobOffer(models.Model):
    """One job offer of an employer."""

    objects = OfferQuerySet.as_manager()

    # ── The choices ───────────────────────────────────────────────────
    # The value stored (left) never changes; the label (right) is for the
    # admin site, the frontend shows its own translated texts

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"

    class Contract(models.TextChoices):
        PERMANENT = "permanent", "Permanent"
        FIXED_TERM = "fixed_term", "Fixed term"
        INTERNSHIP = "internship", "Internship"
        STUDENT = "student", "Student job"

    class Remote(models.TextChoices):
        ON_SITE = "on_site", "On site"
        HYBRID = "hybrid", "Hybrid"
        REMOTE = "remote", "Remote"

    class SalaryPeriod(models.TextChoices):
        MONTH = "month", "Per month"
        YEAR = "year", "Per year"

    class Currency(models.TextChoices):
        CHF = "CHF", "Swiss franc"
        EUR = "EUR", "Euro"

    # ── Who and what ──────────────────────────────────────────────────
    # The offers of an employer are deleted with their profile. From the
    # profile: profile.offers
    employer = models.ForeignKey(
        EmployerProfile,
        on_delete=models.CASCADE,
        related_name="offers",
    )
    title = models.CharField(max_length=200)
    description = models.TextField()

    # ── Where ─────────────────────────────────────────────────────────
    city = models.CharField(max_length=100)
    # ISO 3166-1 code, same list as the profiles; required: the public
    # search filters by country
    country = CountryField()
    remote = models.CharField(
        max_length=10,
        choices=Remote.choices,
        default=Remote.ON_SITE,
    )

    # ── The conditions ────────────────────────────────────────────────
    contract = models.CharField(max_length=12, choices=Contract.choices)
    # Workload as a range of percentages, "80–100 %" the Swiss way; both
    # optional, and min <= max when both are given (constraint below)
    workload_min = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(10), MaxValueValidator(100)],
    )
    workload_max = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(10), MaxValueValidator(100)],
    )
    # Gross salary as a range, per month or per year, in francs or in euros
    # (an offer in France: decision of 20.10.2026); both amounts optional,
    # min <= max when both are given
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    salary_period = models.CharField(
        max_length=5,
        choices=SalaryPeriod.choices,
        default=SalaryPeriod.MONTH,
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.CHF,
    )
    experience_years = models.PositiveSmallIntegerField(null=True, blank=True)

    # ── The life of the offer ─────────────────────────────────────────
    status = models.CharField(
        max_length=9,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    # Set by save() when the offer becomes published (again, when it is
    # reopened): the public list is sorted and filtered by it
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Newest first, wherever the offers are listed without another order
        ordering = ["-created_at"]
        constraints = [
            # The database refuses what the forms and the API check first:
            # a range reversed. Nothing about the titles: an employer may
            # post the same title twice, in two cities (decision of
            # 20.10.2026)
            models.CheckConstraint(
                condition=(
                    Q(salary_min__isnull=True)
                    | Q(salary_max__isnull=True)
                    | Q(salary_min__lte=F("salary_max"))
                ),
                name="offer_salary_min_lte_max",
                violation_error_message="The maximum salary must be at least the minimum.",
            ),
            models.CheckConstraint(
                condition=(
                    Q(workload_min__isnull=True)
                    | Q(workload_max__isnull=True)
                    | Q(workload_min__lte=F("workload_max"))
                ),
                name="offer_workload_min_lte_max",
                violation_error_message="The maximum workload must be at least the minimum.",
            ),
        ]

    def __str__(self):
        return self.title

    # ── The date of publication ───────────────────────────────────────
    # Whoever changes the status (the API, the admin site), the date
    # follows: the model remembers the status it was loaded with, and
    # save() stamps published_at when the offer becomes published

    @classmethod
    def from_db(cls, db, field_names, values):
        """Called by Django for every row read: keeps the status read."""
        offer = super().from_db(db, field_names, values)
        offer._loaded_status = offer.status if "status" in field_names else None
        return offer

    def save(self, *args, **kwargs):
        """Stamps the publication when the offer is published, or published
        again after a draft or a closure; an edit of a published offer
        keeps its date."""
        was_published = getattr(self, "_loaded_status", None) == self.Status.PUBLISHED
        is_published = self.status == self.Status.PUBLISHED
        if is_published and (self.published_at is None or not was_published):
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
        self._loaded_status = self.status

    def clean(self):
        """Checks that need more than one field, with a message per field.

        Called by the admin site and by full_clean(); the API serializer
        does the same checks in its own validate()."""
        errors = {}
        if self.salary_min and self.salary_max and self.salary_min > self.salary_max:
            errors["salary_max"] = _("The maximum must be at least the minimum.")
        if self.workload_min and self.workload_max and self.workload_min > self.workload_max:
            errors["workload_max"] = _("The maximum must be at least the minimum.")
        if errors:
            raise ValidationError(errors)
