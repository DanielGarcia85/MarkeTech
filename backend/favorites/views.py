# backend/favorites/views.py

"""
Favorite views — the API of the favorites
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Answer the requests about the favorites of a candidate: the list, putting
an offer aside, taking it back. Decides who may do what; the shape of the
data is in serializers.py. The "favorite" flag of every offer, which draws
the heart, is given by the offers API (offers/views.py), from this table.

Routes (favorites/urls.py, under /api/, built by the router)
────────────────────────────────────────────────────────────
  GET     favorites/              candidate: their favorites, newest first
  POST    favorites/              candidate: put an offer aside ({"offer"})
  DELETE  favorites/<offer id>/   candidate: take it back, by the offer

Who may do what
───────────────
Everything needs a logged-in candidate: a visitor or an employer gets 403.
A candidate only ever reaches their own favorites: taking back an offer
that is not among them answers 404. The offers of an account the
administrator blocked are left out of the list, until it is unblocked. The deletion is keyed by the offer,
not by the favorite: that is what a heart on a card knows.
"""

from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from applications.views import candidate_profile_of
from offers.views import IsCandidate

from .models import Favorite
from .serializers import AddFavoriteSerializer, FavoriteSerializer


class FavoriteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """The favorites of the logged-in candidate: list, add, remove."""

    permission_classes = [IsCandidate]
    # favorites/<offer id>/: the row is found by its offer
    lookup_field = "offer"
    lookup_value_regex = r"\d+"

    def get_queryset(self):
        """One's own favorites, with the offer and its employer loaded for
        the cards, in a single query."""
        return Favorite.objects.filter(
            candidate__user=self.request.user, offer__employer__user__is_active=True
        ).select_related("offer__employer__user")

    def get_serializer_class(self):
        return AddFavoriteSerializer if self.action == "create" else FavoriteSerializer

    def get_serializer_context(self):
        """The profile of the candidate, for the check and the creation."""
        context = super().get_serializer_context()
        if self.action == "create":
            context["profile"] = candidate_profile_of(self.request.user)
        return context

    def create(self, request, *args, **kwargs):
        """Put an offer aside: the answer is the new favorite as the list
        shows it."""
        form = self.get_serializer(data=request.data)
        form.is_valid(raise_exception=True)
        favorite = form.save()
        data = FavoriteSerializer(favorite, context=self.get_serializer_context()).data
        return Response(data, status=status.HTTP_201_CREATED)
