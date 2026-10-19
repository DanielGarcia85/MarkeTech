# backend/profiles/models.py

"""
Profile models — what a candidate or an employer says about themselves
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Define the profile of each role, one record per user, and the files that go
with it: contact details, photo and CV for a candidate, plus any further
document; contact details, photo, company and logo for an employer. The
account itself (address, password, names, role) stays in the accounts
application.

Why two models and not one
──────────────────────────
The two roles share their contact details but nothing else: a candidate has
a CV and documents, an employer has a company. Two tables keep each one
simple, and a user has one profile or the other, never both. The shared
fields are written once, in an abstract model.

What is not here
────────────────
No name and no e-mail address (the account holds them), no date of birth, no
premium status (decisions of 16 and 18.10.2026). Every field is optional:
the profile is created empty at sign-up and completed later.
"""

from django.conf import settings
from django.db import models
from django_countries.fields import CountryField

from .validators import (
    validate_attachment_extension,
    validate_document_extension,
    validate_file_size,
    validate_image_extension,
)

# ── Storage paths ─────────────────────────────────────────────────────
# Where each kind of file goes, under MEDIA_ROOT. The first folder says who
# may read the file and the second names the user: the view that serves
# the files reads the rights from there. candidates/ and employers/ are for
# the account itself (photos, CV, documents); logos/ is public, a logo
# being shown with the job offers. Django cleans the file name and adds a
# suffix when the name already exists.


def candidate_file_path(profile, filename):
    """Files of a candidate: candidates/<user id>/<file name>."""
    return f"candidates/{profile.user_id}/{filename}"


def candidate_document_path(document, filename):
    """Documents of a candidate: candidates/<user id>/documents/<file name>."""
    return f"candidates/{document.candidate.user_id}/documents/{filename}"


def employer_file_path(profile, filename):
    """Private files of an employer: employers/<user id>/<file name>."""
    return f"employers/{profile.user_id}/{filename}"


def employer_logo_path(profile, filename):
    """Logo of the company, public: logos/<user id>/<file name>."""
    return f"logos/{profile.user_id}/{filename}"


# ── Models ────────────────────────────────────────────────────────────


class ContactDetails(models.Model):
    """Fields shared by the two profiles. Abstract: no table of its own."""

    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True)
    # The two-letter ISO 3166-1 code of the country (CH, FR, ...), checked
    # against the list of django-countries; the name comes from that list,
    # in the language of the request
    country = CountryField(blank=True)

    # Set by Django at every save
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CandidateProfile(ContactDetails):
    """Profile of a candidate: contact details, photo and CV."""

    # One profile per user, deleted with the account. The name after
    # related_name is how the profile is reached from the user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidate_profile",
    )
    photo = models.ImageField(
        upload_to=candidate_file_path,
        blank=True,
        validators=[validate_image_extension, validate_file_size],
    )
    cv = models.FileField(
        upload_to=candidate_file_path,
        blank=True,
        validators=[validate_document_extension, validate_file_size],
    )

    def __str__(self):
        return f"Candidate profile of {self.user.email}"


class CandidateDocument(models.Model):
    """One further document of a candidate: a certificate, a letter..."""

    # Deleted with the profile. From the profile: profile.documents
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    file = models.FileField(
        upload_to=candidate_document_path,
        validators=[validate_attachment_extension, validate_file_size],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Oldest first, wherever the documents are listed
        ordering = ["uploaded_at"]

    def __str__(self):
        return self.file.name


class EmployerProfile(ContactDetails):
    """Profile of an employer: contact details, photo and company."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employer_profile",
    )
    # The photo of the person, private like a candidate's (decision of
    # 19.10.2026): shown to the other side of a conversation one day
    photo = models.ImageField(
        upload_to=employer_file_path,
        blank=True,
        validators=[validate_image_extension, validate_file_size],
    )

    # The company is part of the profile: one employer, one company. Empty
    # at sign-up; the name becomes required to publish a job offer
    company_name = models.CharField(max_length=200, blank=True)
    company_address = models.CharField(max_length=200, blank=True)
    company_postal_code = models.CharField(max_length=10, blank=True)
    company_city = models.CharField(max_length=100, blank=True)
    company_country = CountryField(blank=True)
    company_phone = models.CharField(max_length=30, blank=True)
    logo = models.ImageField(
        upload_to=employer_logo_path,
        blank=True,
        validators=[validate_image_extension, validate_file_size],
    )

    def __str__(self):
        return f"Employer profile of {self.user.email}"
