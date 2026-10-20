# backend/applications/serializers.py

"""
Application serializers — the JSON shape of a job application
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Turn a job application into JSON for the API, and read what a candidate
sends to apply: the offer, a CV (sent, or copied from the profile), an
optional cover letter and the documents of the profile to join. Contains
no view: views.py decides who may do what, and changes the status.

What the JSON looks like
────────────────────────
"offer": what the lists need of the offer (title, city, state, company),
read at the time of the answer. "candidate": the name and the contact
details, read on the account and the profile, never copied. "cv",
"cover_letter" and "attachments": a name to show and the URL of the
applications API that serves the file (the files are not under the public
media URL: the API checks who asks). "status" and "history": the state and
every state the application went through, oldest first. The status is read
only here: it moves through its own route.

How a candidate applies
───────────────────────
A multipart form: "offer" (its id; published offers only), then either
"cv" (a file) or "use_profile_cv" (true: the CV of the profile is copied),
"cover_letter" (a file, optional) and "documents" (ids of the documents of
the profile, repeated: documents=3&documents=5, optional). The files are
copied into the folder of the application; the row and its copies are made
together, or not at all.
"""

import os

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.reverse import reverse

from offers.models import JobOffer

from .models import Attachment, JobApplication

# ── Reading ───────────────────────────────────────────────────────────


def file_json(name, url):
    """A file as the JSON gives it: its name without its folders, and the
    URL that serves it."""
    return {"name": os.path.basename(name), "url": url}


class JobApplicationSerializer(serializers.ModelSerializer):
    """A job application, for the candidate as for the employer."""

    offer = serializers.SerializerMethodField()
    candidate = serializers.SerializerMethodField()
    cv = serializers.SerializerMethodField()
    cover_letter = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "offer",
            "candidate",
            "cv",
            "cover_letter",
            "attachments",
            "status",
            "history",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_offer(self, application):
        """The offer as the lists show it, the company read on the profile."""
        offer = application.offer
        return {
            "id": offer.pk,
            "title": offer.title,
            "city": offer.city,
            "status": offer.status,
            "company": {"name": offer.employer.company_name},
        }

    def get_candidate(self, application):
        """The name and the contact details of the candidate, as the account
        and the profile say them today; no photo (decision of 20.10.2026)."""
        profile = application.candidate
        user = profile.user
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": profile.phone,
            "city": profile.city,
        }

    def get_cv(self, application):
        return file_json(
            application.cv.name,
            reverse("application-cv", args=[application.pk]),
        )

    def get_cover_letter(self, application):
        if not application.cover_letter:
            return None
        return file_json(
            application.cover_letter.name,
            reverse("application-cover-letter", args=[application.pk]),
        )

    def get_attachments(self, application):
        return [
            {
                "id": attachment.pk,
                **file_json(
                    attachment.file.name,
                    reverse("application-attachment", args=[application.pk, attachment.pk]),
                ),
            }
            for attachment in application.attachments.all()
        ]

    def get_history(self, application):
        """Every state the application went through, oldest first."""
        return [
            {"status": change.status, "changed_at": change.changed_at}
            for change in application.history.all()
        ]


# ── Applying ──────────────────────────────────────────────────────────


def copy_of(field_file):
    """The content of a stored file, as a new file to store elsewhere: Django
    writes it under the path of the receiving field when the row is saved.
    Read whole (5 MB at most) and closed at once: an open file cannot be
    deleted on Windows."""
    with field_file.open("rb") as source:
        return ContentFile(source.read(), name=os.path.basename(field_file.name))


class ApplySerializer(serializers.Serializer):
    """What a candidate sends to apply. Needs the candidate profile in its
    context: the view passes it as "profile"."""

    # Published offers only: a draft, a closed offer or no offer at all get
    # the same answer, the API does not say what exists
    offer = serializers.PrimaryKeyRelatedField(
        queryset=JobOffer.objects.filter(status=JobOffer.Status.PUBLISHED),
        error_messages={
            "does_not_exist": "This offer is not open to applications.",
            "incorrect_type": "This offer is not open to applications.",
        },
    )
    cv = serializers.FileField(required=False)
    use_profile_cv = serializers.BooleanField(default=False)
    cover_letter = serializers.FileField(required=False)
    documents = serializers.ListField(child=serializers.IntegerField(), required=False)

    @property
    def profile(self):
        return self.context["profile"]

    def validate_cv(self, cv):
        """The checks of the model field (type, size), on the sent file."""
        JobApplication._meta.get_field("cv").run_validators(cv)
        return cv

    def validate_cover_letter(self, letter):
        JobApplication._meta.get_field("cover_letter").run_validators(letter)
        return letter

    def validate_documents(self, ids):
        """The documents of this profile only, each at most once."""
        ids = list(dict.fromkeys(ids))
        documents = list(self.profile.documents.filter(pk__in=ids))
        if len(documents) != len(ids):
            raise serializers.ValidationError("Unknown document.")
        return documents

    def validate(self, data):
        """A CV, one way or the other; one application per offer."""
        if data["use_profile_cv"]:
            if not self.profile.cv:
                raise serializers.ValidationError({"cv": ["Your profile has no CV."]})
        elif "cv" not in data:
            raise serializers.ValidationError({"cv": ["A CV is required."]})
        if JobApplication.objects.filter(offer=data["offer"], candidate=self.profile).exists():
            raise serializers.ValidationError("You have already applied to this offer.")
        return data

    def create(self, data):
        """The application and the copies of its files, all or nothing."""
        cv = copy_of(self.profile.cv) if data["use_profile_cv"] else data["cv"]
        with transaction.atomic():
            application = JobApplication.objects.create(
                offer=data["offer"],
                candidate=self.profile,
                cv=cv,
                cover_letter=data.get("cover_letter", ""),
            )
            for document in data.get("documents", []):
                Attachment.objects.create(application=application, file=copy_of(document.file))
        return application
