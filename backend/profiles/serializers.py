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
Every text field of the model, as it is, plus the names and the address of
the account: the names can be changed here, the address is read only (it
changes through allauth, with a confirmation e-mail); and the language and
the choice of notifications of the account (accounts/models.py), changed
here too: by the language selector and the page of the credentials. A country is its
two-letter code (CH), or "" for none; the names are served by the
countries route. A file field is the URL of the file (MEDIA_URL plus its
path, relative to the site), or null.
The documents of a candidate are a list inside the profile, read only: they
are added and removed by their own routes.
"""

import os

from django.conf import settings
from django.db import models
from django_countries.serializers import CountryFieldMixin
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


class FileSerializer(serializers.ModelSerializer):
    """What every serializer of this file shares: the URL of the files, and
    the removal of an old file when a new one replaces it."""

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


class ProfileSerializer(CountryFieldMixin, FileSerializer):
    """What the two profiles share: the names and the address of the
    account, shown with the profile and, for the names, changed with it.
    The mixin of django-countries represents a country field by its code
    (CH); on the way in it accepts a code or a name of the list (in the
    language of the request, or in English), stores the code, and refuses
    anything else."""

    # Read from the user behind the profile, and written back to it. Same
    # rules as at sign-up: required, 150 characters at most
    first_name = serializers.CharField(source="user.first_name", max_length=150)
    last_name = serializers.CharField(source="user.last_name", max_length=150)
    email = serializers.EmailField(source="user.email", read_only=True)
    # The language of the notifications, one the site offers, and whether
    # they go (decisions of 26.10.2026)
    language = serializers.ChoiceField(source="user.language", choices=settings.LANGUAGES)
    notify_by_email = serializers.BooleanField(source="user.notify_by_email")

    # Fields of the account, listed by the two subclasses before their own
    ACCOUNT_FIELDS = ("first_name", "last_name", "email", "language", "notify_by_email")

    def update(self, instance, validated_data):
        """Save the profile, and the names on the account when they are sent
        (DRF puts the fields with a "user." source under one "user" key)."""
        user_data = validated_data.pop("user", None)
        instance = super().update(instance, validated_data)
        if user_data:
            for name, value in user_data.items():
                setattr(instance.user, name, value)
            instance.user.save(update_fields=list(user_data))
        return instance


class CandidateDocumentSerializer(FileSerializer):
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
        fields = ProfileSerializer.ACCOUNT_FIELDS + (
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

    file_fields = ("photo", "logo")

    class Meta:
        model = EmployerProfile
        fields = ProfileSerializer.ACCOUNT_FIELDS + (
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
            "photo",
            "logo",
            "updated_at",
        )
        read_only_fields = ("updated_at",)
