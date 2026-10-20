# backend/applications/models.py

"""
Job application models — a candidate applying to an offer
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Define a job application: who applies to which offer, with which files (a
CV, an optional cover letter, documents taken from the profile), and where
it stands with the employer. Three models: the application itself, the
history of its states, and its attachments. An application belongs to one
candidate profile and to one offer, and goes away with either.

What is not here
────────────────
The name and the contact details of the candidate: they are read on the
account and the profile whenever the application is shown, like the company
of an offer. Nor the rules of the API (who may read, apply, withdraw, change
a state): they live in the views and serializers.

The files are copies
────────────────────
The CV, the letter and the documents are copied into the application when
it is sent, never referenced on the profile: a candidate who replaces or
removes a file of their profile afterwards does not change what the
employer received. Decisions of 20.10.2026.

The states
──────────
received: just sent, the only state an application is created in.
in_progress, accepted, rejected: set by the employer. Every state the
application goes through is recorded in its history by save(), whoever
changes it (the API, the admin site): the original project had the table
and never filled it.
"""

from django.db import models

from offers.models import JobOffer
from profiles.models import CandidateProfile
from profiles.validators import (
    validate_attachment_extension,
    validate_document_extension,
    validate_file_size,
)

# ── Storage paths ─────────────────────────────────────────────────────
# Where the files of an application go, under MEDIA_ROOT: one folder per
# application, named after the candidate and the offer, which are unique
# together (constraint below) and known before the row exists (Django
# computes the path before the INSERT, when the application has no id yet).
# The folder is not under candidates/: the file view of the profiles does
# not know it, and answers "not found"; the applications API serves these
# files itself, to the candidate and to the employer of the offer.


def application_file_path(application, filename):
    """CV and cover letter: applications/<user id>/<offer id>/<file name>."""
    return f"applications/{application.candidate.user_id}/{application.offer_id}/{filename}"


def attachment_path(attachment, filename):
    """Documents joined: applications/<user id>/<offer id>/documents/<file name>."""
    application = attachment.application
    folder = f"applications/{application.candidate.user_id}/{application.offer_id}"
    return f"{folder}/documents/{filename}"


# ── Models ────────────────────────────────────────────────────────────


class JobApplication(models.Model):
    """One application of a candidate to one offer."""

    # The value stored (left) never changes; the label (right) is for the
    # admin site, the frontend shows its own translated texts
    class Status(models.TextChoices):
        RECEIVED = "received", "Received"
        IN_PROGRESS = "in_progress", "In progress"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    # ── Who and to what ───────────────────────────────────────────────
    # Deleted with the offer, and with the profile of the candidate. From
    # the offer: offer.applications; from the profile: profile.applications
    offer = models.ForeignKey(
        JobOffer,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    # ── The files ─────────────────────────────────────────────────────
    # Same kinds and same size limit as the files of the profiles
    cv = models.FileField(
        upload_to=application_file_path,
        validators=[validate_document_extension, validate_file_size],
    )
    cover_letter = models.FileField(
        upload_to=application_file_path,
        blank=True,
        validators=[validate_document_extension, validate_file_size],
    )

    # ── The life of the application ───────────────────────────────────
    status = models.CharField(
        max_length=11,
        choices=Status.choices,
        default=Status.RECEIVED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Newest first, wherever the applications are listed
        ordering = ["-created_at"]
        constraints = [
            # One application per candidate and per offer, refused by the
            # database itself: the original project checked it in a view
            # only
            models.UniqueConstraint(
                fields=["offer", "candidate"],
                name="one_application_per_offer_and_candidate",
                violation_error_message="You have already applied to this offer.",
            ),
        ]

    def __str__(self):
        return f"Application {self.pk} to {self.offer}"

    # ── The history ───────────────────────────────────────────────────
    # Whoever changes the status (the API, the admin site), the history
    # follows: the model remembers the status it was loaded with, and
    # save() records a change when the status is new or different

    @classmethod
    def from_db(cls, db, field_names, values):
        """Called by Django for every row read: keeps the status read."""
        application = super().from_db(db, field_names, values)
        application._loaded_status = application.status if "status" in field_names else None
        return application

    def save(self, *args, **kwargs):
        """Saves, then records the state in the history when the application
        is new, or when its status changed since it was loaded."""
        changed = self._state.adding or self.status != getattr(self, "_loaded_status", None)
        super().save(*args, **kwargs)
        if changed:
            self.history.create(status=self.status)
        self._loaded_status = self.status


class StatusChange(models.Model):
    """One state an application went through, and when."""

    # Deleted with the application. From the application: application.history
    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="history",
    )
    status = models.CharField(max_length=11, choices=JobApplication.Status.choices)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Oldest first: the history reads as a timeline
        ordering = ["changed_at", "pk"]

    def __str__(self):
        return f"{self.get_status_display()} on {self.changed_at:%Y-%m-%d}"


class Attachment(models.Model):
    """One document of the profile joined to an application, as a copy."""

    # Deleted with the application. From the application:
    # application.attachments
    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(
        upload_to=attachment_path,
        validators=[validate_attachment_extension, validate_file_size],
    )

    class Meta:
        # In the order they were joined
        ordering = ["pk"]

    def __str__(self):
        return self.file.name
