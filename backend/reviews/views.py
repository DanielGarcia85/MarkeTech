# backend/reviews/views.py

"""
Reviews views — the API of the reviews
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Answer the requests about the reviews: all of them, for anyone, with their
averages; the review of the user, to write, rewrite or delete it. Decides
who may do what; the shape of the data is in serializers.py.

Routes (reviews/urls.py, under /api/)
─────────────────────────────────────
  GET     reviews/        public: the reviews, newest first, ten a page
                          (?page=2, ?page_size=3 for the side bar, fifty at
                          most), and their summary: how many, the average
                          of each score, how many gave each rating
  GET     reviews/mine/   the review of the user; 204, no content, before it
                          is written (a normal state, not an error: a 404
                          would fill the logs at every visit)
  PUT     reviews/mine/   {rating, ease_of_use, offers_and_applications,
                          messaging, appointments, comment}: writes it
                          (201) or rewrites it (200)
  DELETE  reviews/mine/   deletes it (204)

Who may do what
───────────────
Anyone reads the reviews, logged in or not. A candidate or an employer has
one review; an administrator, who has no role, has none (403), and the
list leaves out any review of an account without a role, and of an account
the administrator blocked (is_active unticked in the admin: the review
comes back when the account is unblocked; decision of 26.10.2026). A demo account,
open to every visitor, reads its review but may not change it (403): the
reviews are public, and a visitor would otherwise write in the name of the
platform until the night.

The administrator is told
─────────────────────────
A review is public as soon as it is written: each one written or rewritten
is sent by e-mail to the administrator, who may delete it from the admin
(notifications/moderation.py; decisions of 26.10.2026).
"""

from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from notifications import moderation

from .models import CRITERIA, HIGHEST, LOWEST, Review
from .serializers import ReviewSerializer, WriteSerializer

# The roles that review the platform
AUTHORS = [User.Role.CANDIDATE, User.Role.EMPLOYER]


def public():
    """The reviews shown: those of a candidate or an employer whose account
    is not blocked, with the author and the profile of an employer, which
    the JSON reads."""
    return Review.objects.filter(user__role__in=AUTHORS, user__is_active=True).select_related(
        "user", "user__employer_profile"
    )


def summary(reviews):
    """How many reviews, the average of each score to one decimal (None
    without reviews), and how many gave each rating, from 5 down to 1."""
    averages = reviews.aggregate(
        rating=Avg("rating"), **{field: Avg(field) for field in CRITERIA}
    )
    counts = dict(
        reviews.order_by().values_list("rating").annotate(count=Count("pk"))
    )
    return {
        "count": sum(counts.values()),
        "averages": {
            field: None if value is None else round(value, 1)
            for field, value in averages.items()
        },
        "ratings": {str(rating): counts.get(rating, 0) for rating in range(HIGHEST, LOWEST - 1, -1)},
    }


class ReviewPagination(PageNumberPagination):
    """Pages of ten, ?page=2; the side bar asks for three with
    ?page_size=3, fifty at most."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class ReviewListView(ListAPIView):
    """The reviews, for anyone, with their summary next to the page."""

    permission_classes = [permissions.AllowAny]
    serializer_class = ReviewSerializer
    pagination_class = ReviewPagination

    def get_queryset(self):
        return public()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data["summary"] = summary(public())
        return response


class MyReviewView(APIView):
    """The review of the user: read, write or rewrite, delete."""

    permission_classes = [permissions.IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        """Only a candidate or an employer has a review; a demo account
        reads its own and changes nothing."""
        super().initial(request, *args, **kwargs)
        user = request.user
        if user.role not in AUTHORS:
            raise PermissionDenied(_("Only a candidate or an employer reviews the platform."))
        if user.is_demo and request.method not in permissions.SAFE_METHODS:
            raise PermissionDenied(_("A demo account cannot publish a review."))

    def answer(self, request, review, code=status.HTTP_200_OK):
        data = ReviewSerializer(review, context={"request": request}).data
        return Response(data, status=code)

    def get(self, request):
        review = public().filter(user=request.user).first()
        if review is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return self.answer(request, review)

    def put(self, request):
        form = WriteSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        # One review per account: the database refuses a second, and
        # update_or_create reads again the one a request at the same
        # moment would have written
        review, created = Review.objects.update_or_create(
            user=request.user, defaults=form.validated_data
        )
        review = public().get(pk=review.pk)
        moderation.review_written(request, review, created)
        return self.answer(request, review, status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request):
        get_object_or_404(Review, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
