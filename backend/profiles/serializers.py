# backend/profiles/serializers.py

"""
Profile serializers — the JSON shape of the profiles and the documents
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Turn a profile into JSON for the API, and read back what the frontend sends,
field by field, with the checks of the model (lengths, size and type of the
files). Replace a file properly: the old one leaves the disk before the new
one is stored. Contains no view: views.py decides who may do what.

What the JSON looks like
────────────────────────
Every text field of the model, as it is. A file field is the URL of the file
(MEDIA_URL plus its path, relative to the site), or null. The documents of a
candidate are a list inside the profile, read only: they are added and
removed by their own routes. The account itself (names, address, role) is
not here: the session API of allauth gives it.
"""

import os

from django.db import models
from rest_framework import serializers

from .models import CandidateDocument, CandidateProfile, EmployerProfile

# ── File fields ───────────────────────────────────────────────────────


class RelativeUrlMixin:
    """A file given as the URL of the site (/api/files/...), never absolute."""

    def to_representation(self, value):
        # The default builds http://host/... from the request; the frontend
        # lives on the same site, a relative URL works everywhere
        return value.url if value else None


class FileUrlField(RelativeUrlMixin, serializers.FileField):
    pass


class ImageUrlField(RelativeUrlMixin, serializers.ImageField):
    pass


# ── Serializers ───────────────────────────────────────────────────────


class ProfileSerializer(serializers.ModelSerializer):
    """What the two profile serializers share: the URL of the files, and the
    removal of an old file when a new one replaces it."""

    # Which serializer field represents which model field: the two file
    # types get the relative-URL variants, the rest keeps DRF's defaults
    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        models.FileField: FileUrlField,
        models.ImageField: ImageUrlField,
    }

    # Names of the file fields of the model, given by each subclass
    file_fields = ()

    def update(self, instance, validated_data):
        """Save the changes; a file that is replaced is first deleted."""
        for name in self.file_fields:
            if name in validated_data:
                old = getattr(instance, name)
                if old:
                    # Removed from the disk now: Django would keep it, and
                    # nothing would ever point to it again
                    old.delete(save=False)
        return super().update(instance, validated_data)


class CandidateDocumentSerializer(ProfileSerializer):
    """One further document of a candidate."""

    file_fields = ("file",)

    # The name shown in the list: the file name without its folders
    name = serializers.SerializerMethodField()

    class Meta:
        model = CandidateDocument
        fields = ("id", "name", "file", "uploaded_at")
        read_only_fields = ("id", "uploaded_at")

    def get_name(self, document):
        return os.path.basename(document.file.name)


class CandidateProfileSerializer(ProfileSerializer):
    """Profile of a candidate, documents included."""

    file_fields = ("photo", "cv")

    documents = CandidateDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = CandidateProfile
        fields = (
            "phone",
            "address",
            "postal_code",
            "city",
            "country",
            "photo",
            "cv",
            "documents",
            "updated_at",
        )
        read_only_fields = ("updated_at",)


class EmployerProfileSerializer(ProfileSerializer):
    """Profile of an employer, company included."""

    file_fields = ("logo",)

    class Meta:
        model = EmployerProfile
        fields = (
            "phone",
            "address",
            "postal_code",
            "city",
            "country",
            "company_name",
            "company_address",
            "company_postal_code",
            "company_city",
            "company_country",
            "company_phone",
            "logo",
            "updated_at",
        )
        read_only_fields = ("updated_at",)
