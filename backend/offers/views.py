# backend/offers/views.py

"""
Offer views — the API of the job offers
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Answer the requests about the job offers: the public list and the detail of
a published offer, for anyone; and for an employer, their own offers in any
state, their creation, their edition, their deletion, and the two moves of
their state, publish and close. Decides who may do what and applies the
rules of the state; the shape of the data is in serializers.py.

Routes (offers/urls.py, under /api/, built by the router)
─────────────────────────────────────────────────────────
  GET     offers/               published offers: filters, order, pages
  GET     offers/<id>/          one published offer, or one's own
  GET     offers/mine/          employer: all of their offers
  POST    offers/               employer: a new offer, as a draft
  PATCH   offers/<id>/          employer: change one of theirs
  DELETE  offers/<id>/          employer: delete one of theirs
  POST    offers/<id>/publish/  employer: draft or closed -> published
  POST    offers/<id>/close/    employer: published -> closed

An offer that received applications is not deleted (the candidates would
lose their trace): closed instead. A published offer is closed before it
is deleted. The employer's answers carry the numbers
of applications received and of favorites, the public ones do not; the
detail of an offer carries them for its own employer only. For a candidate,
every offer says whether they put it aside ("favorite", the heart).

Who may do what
───────────────
Reading the list and a published offer is public. Everything else needs a
logged-in employer: a visitor or a candidate gets 403. An employer only ever
reaches their own offers: another one's answers 404, never 403 (the API
does not say what exists), and a draft or a closed offer is 404 for the
public, as is any offer of an account the administrator blocked
(models.py).

The administrator is told
─────────────────────────
An offer published, or changed while it is published, is public at once:
an e-mail tells the administrator, who may remove it from the admin
(notifications/moderation.py; decisions of 26.10.2026).

Why a ModelViewSet
──────────────────
An offer is the plain CRUD resource of REST. The ModelViewSet of DRF writes
the five handlers once (list, retrieve, create, update, destroy) from a
queryset and a serializer, the router derives the routes, and the two extra
moves are added as actions. The whole decision is in get_queryset() and in
get_permissions().
"""

from django.db.models import Count, Exists, OuterRef, Q
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.utils.translation import gettext as _
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from accounts.models import User
from favorites.models import Favorite
from profiles.models import EmployerProfile

from notifications import moderation

from .models import JobOffer, public_offer
from .serializers import JobOfferSerializer, MyOfferSerializer

# ── Who ───────────────────────────────────────────────────────────────


def is_employer(user):
    """A logged-in user whose role is employer."""
    return user.is_authenticated and user.role == User.Role.EMPLOYER


def is_candidate(user):
    """A logged-in user whose role is candidate."""
    return user.is_authenticated and user.role == User.Role.CANDIDATE


class IsEmployer(permissions.BasePermission):
    """The same, as a permission for the views."""

    def has_permission(self, request, view):
        return is_employer(request.user)


class IsCandidate(permissions.BasePermission):
    """A logged-in candidate, as a permission for the views (used by the
    applications and the favorites)."""

    def has_permission(self, request, view):
        return is_candidate(request.user)


def employer_profile_of(user):
    """The employer profile of the user, created empty when missing (an
    account made in the admin site), like the profiles API does."""
    profile, _created = EmployerProfile.objects.get_or_create(user=user)
    return profile


# ── How many ──────────────────────────────────────────────────────────


class OfferPagination(PageNumberPagination):
    """Pages of ten, ?page=2; the caller may ask for up to fifty with
    ?page_size=50. The answer carries count, next, previous and results."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


# ── The offers ────────────────────────────────────────────────────────


class JobOfferViewSet(viewsets.ModelViewSet):
    """The job offers: public reading, and the management by their employer."""

    serializer_class = JobOfferSerializer
    pagination_class = OfferPagination
    # ?ordering=-published_at (the default), title, salary_min, -salary_max...
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["published_at", "title", "salary_min", "salary_max"]
    ordering = ["-published_at"]
    # Only PATCH changes an offer: PUT would demand every field each time
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):
        """Public reading; an employer for everything else."""
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [IsEmployer()]

    def get_serializer_class(self):
        """The public shape for the reading, the employer's shape (with the
        number of applications) for everything else."""
        if self.action in ("list", "retrieve"):
            return JobOfferSerializer
        return MyOfferSerializer

    def retrieve(self, request, *args, **kwargs):
        """One offer: the employer's shape for their own, the public shape
        for anybody else's (the count is not for the competition)."""
        offer = self.get_object()
        shape = MyOfferSerializer if offer.employer.user_id == request.user.pk else JobOfferSerializer
        return Response(shape(offer, context=self.get_serializer_context()).data)

    def get_queryset(self):
        """What the request may see, before any filter of the list."""
        offers = JobOffer.objects.select_related("employer__user")
        user = self.request.user
        if is_candidate(user):
            # Whether the candidate put each offer aside, in the same query
            # (a sub-query per row, not a request per card)
            put_aside = Favorite.objects.filter(offer=OuterRef("pk"), candidate__user=user)
            offers = offers.annotate(favorite=Exists(put_aside))
        mine = Q(employer__user=user) if is_employer(user) else Q(pk__in=[])
        if self.action == "list":
            return self.filtered(offers.public())
        if self.action == "retrieve":
            # A public offer, or one's own in any state
            return offers.filter(public_offer() | mine)
        # mine, update, destroy, publish, close: one's own only
        return offers.filter(mine)

    def filtered(self, offers):
        """The filters of the public list, read in the query string. An
        empty or absent parameter does not filter; a bad one is ignored."""
        params = self.request.query_params
        if title := params.get("title", "").strip():
            offers = offers.filter(title__icontains=title)
        if city := params.get("city", "").strip():
            offers = offers.filter(city__icontains=city)
        if country := params.get("country", "").strip():
            offers = offers.filter(country=country.upper())
        if contract := params.get("contract", "").strip():
            offers = offers.filter(contract=contract)
        if remote := params.get("remote", "").strip():
            offers = offers.filter(remote=remote)
        if (salary := params.get("salary_min", "").strip()).isdigit():
            # At least this much, among the offers that state a salary for
            # the same period and in the same currency (a monthly figure
            # says nothing about a yearly one, nor francs about euros)
            period = params.get("salary_period", JobOffer.SalaryPeriod.MONTH)
            currency = params.get("currency", JobOffer.Currency.CHF).upper()
            amount = int(salary)
            reaches = Q(salary_max__gte=amount) | Q(salary_max__isnull=True, salary_min__gte=amount)
            offers = offers.filter(reaches, salary_period=period, currency=currency)
        if published_after := parse_date(params.get("published_after", "")):
            offers = offers.filter(published_at__date__gte=published_after)
        return offers

    def perform_create(self, serializer):
        """A new offer belongs to the employer who sends it, as a draft."""
        serializer.save(employer=employer_profile_of(self.request.user))

    def perform_update(self, serializer):
        """A change to an offer already published is public at once: the
        administrator is told."""
        offer = serializer.save()
        if offer.status == JobOffer.Status.PUBLISHED:
            moderation.offer_published(self.request, offer, changed=True)

    def perform_destroy(self, offer):
        """Refused once candidates applied: the offer is closed instead, and
        the applications stay with their candidates. Refused too while the
        offer is published: it is closed first, as the page offers it
        (decision of 28.10.2026)."""
        if offer.applications.exists():
            message = _("This offer has received applications: close it instead of deleting it.")
            raise ValidationError({"non_field_errors": [message]})
        if offer.status == JobOffer.Status.PUBLISHED:
            message = _("This offer is published: close it before deleting it.")
            raise ValidationError({"non_field_errors": [message]})
        offer.delete()

    # ── The extra routes ──────────────────────────────────────────────

    @action(detail=False, methods=["get"])
    def mine(self, request):
        """All the offers of the employer, in any state, newest first, each
        with its numbers of applications and of favorites counted by the
        same query (distinct: two joins would multiply the rows); no pages:
        an employer has a handful of offers."""
        offers = self.get_queryset().annotate(
            applications_count=Count("applications", distinct=True),
            favorites_count=Count("favorites", distinct=True),
        )
        offers = offers.order_by("-created_at")
        return Response(self.get_serializer(offers, many=True).data)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Draft or closed -> published. The company must have a name: it
        is what the public list shows above the title."""
        offer = get_object_or_404(self.get_queryset(), pk=pk)
        if offer.status == JobOffer.Status.PUBLISHED:
            raise ValidationError({"non_field_errors": [_("This offer is already published.")]})
        if not offer.employer.company_name.strip():
            # Under "company", so that the page can offer the way to the
            # profile, whatever the language of the text
            message = _("Give the name of your company in your profile before publishing.")
            raise ValidationError({"company": [message]})
        offer.status = JobOffer.Status.PUBLISHED
        offer.save()
        moderation.offer_published(request, offer, changed=False)
        return Response(self.get_serializer(offer).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """Published -> closed: out of the public list, kept by the employer."""
        offer = get_object_or_404(self.get_queryset(), pk=pk)
        if offer.status != JobOffer.Status.PUBLISHED:
            raise ValidationError({"non_field_errors": [_("Only a published offer can be closed.")]})
        offer.status = JobOffer.Status.CLOSED
        offer.save()
        return Response(self.get_serializer(offer).data, status=status.HTTP_200_OK)
