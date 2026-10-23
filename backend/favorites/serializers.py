# backend/favorites/serializers.py

"""
Favorite serializers — the JSON shape of a favorite
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Turn a favorite into JSON for the API, and read what a candidate sends to
put an offer aside. Contains no view: views.py decides who may do what.

What the JSON looks like
────────────────────────
"offer": the offer as the public list gives it (the same shape, the same
serializer), with "favorite" true, so that the page of the favorites draws
the same cards with the same heart; "created_at": when it was put aside.

How a candidate puts an offer aside
───────────────────────────────────
{"offer": <id>}, a published offer only: a draft, a closed offer or no
offer at all get the same answer, the API does not say what exists. Once
per offer.
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from offers.models import JobOffer
from offers.serializers import JobOfferSerializer

from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    """A favorite, with its offer as the cards show it."""

    offer = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ["id", "offer", "created_at"]
        read_only_fields = fields

    def get_offer(self, favorite):
        """The offer as the public list gives it; a favorite's offer is, by
        definition, a favorite of the candidate asking."""
        offer = favorite.offer
        offer.favorite = True
        return JobOfferSerializer(offer, context=self.context).data


class AddFavoriteSerializer(serializers.Serializer):
    """What a candidate sends to put an offer aside. Needs the candidate
    profile in its context: the view passes it as "profile"."""

    offer = serializers.PrimaryKeyRelatedField(
        queryset=JobOffer.objects.filter(status=JobOffer.Status.PUBLISHED),
        error_messages={
            "does_not_exist": _("This offer cannot be put aside."),
            "incorrect_type": _("This offer cannot be put aside."),
        },
    )

    def validate_offer(self, offer):
        """Once per offer."""
        if Favorite.objects.filter(offer=offer, candidate=self.context["profile"]).exists():
            raise serializers.ValidationError(_("This offer is already in your favourites."))
        return offer

    def create(self, data):
        return Favorite.objects.create(offer=data["offer"], candidate=self.context["profile"])
