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

Who may do what
───────────────
Reading the list and a published offer is public. Everything else needs a
logged-in employer: a visitor or a candidate gets 403. An employer only ever
reaches their own offers: another one's answers 404, never 403 (the API
does not say what exists), and a draft or a closed offer is 404 for the
public.

Why a ModelViewSet
──────────────────
An offer is the plain CRUD resource of REST. The ModelViewSet of DRF writes
the five handlers once (list, retrieve, create, update, destroy) from a
queryset and a serializer, the router derives the routes, and the two extra
moves are added as actions. The whole decision is in get_queryset() and in
get_permissions().
"""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from accounts.models import User
from profiles.models import EmployerProfile

from .models import JobOffer
from .serializers import JobOfferSerializer

# ── Who ───────────────────────────────────────────────────────────────


def is_employer(user):
    """A logged-in user whose role is employer."""
    return user.is_authenticated and user.role == User.Role.EMPLOYER


class IsEmployer(permissions.BasePermission):
    """The same, as a permission for the views."""

    def has_permission(self, request, view):
        return is_employer(request.user)


def employer_profile_of(user):
    """The employer profile of the user, created empty when missing (an
    account made in the admin site), like the profiles API does."""
    profile, _ = EmployerProfile.objects.get_or_create(user=user)
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

    def get_queryset(self):
        """What the request may see, before any filter of the list."""
        offers = JobOffer.objects.select_related("employer__user")
        user = self.request.user
        mine = Q(employer__user=user) if is_employer(user) else Q(pk__in=[])
        if self.action == "list":
            return self.filtered(offers.filter(status=JobOffer.Status.PUBLISHED))
        if self.action == "retrieve":
            # A published offer, or one's own in any state
            return offers.filter(Q(status=JobOffer.Status.PUBLISHED) | mine)
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

    # ── The extra routes ──────────────────────────────────────────────

    @action(detail=False, methods=["get"])
    def mine(self, request):
        """All the offers of the employer, in any state, newest first;
        no pages: an employer has a handful of offers."""
        offers = self.get_queryset().order_by("-created_at")
        return Response(self.get_serializer(offers, many=True).data)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Draft or closed -> published. The company must have a name: it
        is what the public list shows above the title."""
        offer = get_object_or_404(self.get_queryset(), pk=pk)
        if offer.status == JobOffer.Status.PUBLISHED:
            raise ValidationError({"non_field_errors": ["This offer is already published."]})
        if not offer.employer.company_name.strip():
            message = "Give the name of your company in your profile before publishing."
            raise ValidationError({"non_field_errors": [message]})
        offer.status = JobOffer.Status.PUBLISHED
        offer.save()
        return Response(self.get_serializer(offer).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """Published -> closed: out of the public list, kept by the employer."""
        offer = get_object_or_404(self.get_queryset(), pk=pk)
        if offer.status != JobOffer.Status.PUBLISHED:
            raise ValidationError({"non_field_errors": ["Only a published offer can be closed."]})
        offer.status = JobOffer.Status.CLOSED
        offer.save()
        return Response(self.get_serializer(offer).data, status=status.HTTP_200_OK)
