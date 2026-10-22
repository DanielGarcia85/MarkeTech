# backend/appointments/models.py

"""
Appointment model — a meeting an employer proposes about an application
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Define an appointment: the application it is about, when it starts, how
long it lasts, where it takes place, what the employer adds, its state,
the answer of the candidate (or the word of a cancellation) and when it
came, and whether the participant concerned by its last change has seen
it (decisions of 22.10.2026).

The rules
─────────
Only the employer of the offer proposes, and only while the application
is in progress; the candidate answers once, accepting or declining, with
a message; the employer may cancel a pending or accepted appointment that
has not taken place. Several appointments per application, but one
pending at a time: the database itself refuses a second one. A proposal
is never changed: the employer cancels it and proposes again.

An appointment still pending when its time has come, or when the
application has been decided, is expired: a state computed here
(is_expired), never written, so that the applications need not touch the
appointments when they change.

Who has news
────────────
seen_at is emptied at every change and set when the participant concerned
opens the appointments or the conversation. That participant follows from
the state: a proposal or a cancellation is news for the candidate, an
answer news for the employer (recipient).

What is not here
────────────────
Who may do what and when (the views), the pages.
"""

from datetime import timedelta

from django.db import models
from django.utils import timezone

from applications.models import JobApplication

# The longest text accepted, as for a message
MAX_LENGTH = 2000


class Appointment(models.Model):
    """One meeting between the candidate and the employer of an application."""

    # The value stored (left) never changes; the label (right) is for the
    # admin site, the frontend shows its own translated texts
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        CANCELLED = "cancelled", "Cancelled"

    # The lengths offered, in minutes
    class Duration(models.IntegerChoices):
        HALF_HOUR = 30, "30 minutes"
        THREE_QUARTERS = 45, "45 minutes"
        HOUR = 60, "1 hour"
        HOUR_AND_HALF = 90, "1 hour 30"

    # ── What it is about ──────────────────────────────────────────────
    # Deleted with the application; from the application:
    # application.appointments. The employer and the candidate are those
    # of the application, not stored a second time
    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    # ── What the employer proposes ────────────────────────────────────
    # Stored in UTC, shown in the time zone of each reader
    starts_at = models.DateTimeField()
    duration = models.PositiveSmallIntegerField(choices=Duration, default=Duration.HOUR)
    # An address, a link to a video call, or "by phone"
    place = models.CharField(max_length=200)
    note = models.TextField(max_length=MAX_LENGTH, blank=True)

    # ── What became of it ─────────────────────────────────────────────
    status = models.CharField(max_length=10, choices=Status, default=Status.PENDING)
    # The message of the candidate, or the word of the employer cancelling
    response = models.TextField(max_length=MAX_LENGTH, blank=True)
    # When the answer or the cancellation came; empty while pending
    answered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Set when the participant concerned by the last change has seen it
    seen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # In the order they take place
        ordering = ["starts_at", "pk"]
        constraints = [
            # One pending appointment per application at a time
            models.UniqueConstraint(
                fields=["application"],
                condition=models.Q(status="pending"),
                name="one_pending_appointment_per_application",
                violation_error_message="This application already has a pending appointment.",
            ),
            # A place to go to, or a way to meet
            models.CheckConstraint(
                condition=~models.Q(place=""),
                name="appointment_place_not_empty",
                violation_error_message="An appointment needs a place.",
            ),
            # An answer of the candidate always says something
            models.CheckConstraint(
                condition=~models.Q(status__in=["accepted", "declined"]) | ~models.Q(response=""),
                name="appointment_answer_has_message",
                violation_error_message="An answer needs a message.",
            ),
            # One of the lengths offered only
            models.CheckConstraint(
                condition=models.Q(duration__in=[30, 45, 60, 90]),
                name="appointment_duration_offered",
                violation_error_message="This length is not offered.",
            ),
        ]

    def __str__(self):
        return f"Appointment {self.pk} on application {self.application_id}"

    @property
    def ends_at(self):
        """When it ends: its start and its length."""
        return self.starts_at + timedelta(minutes=self.duration)

    @property
    def recipient(self):
        """Who the last change is news for: "candidate" or "employer"."""
        if self.status in (self.Status.PENDING, self.Status.CANCELLED):
            return "candidate"
        return "employer"

    def is_expired(self, now=None):
        """Pending, but its time has come or the application is decided."""
        if self.status != self.Status.PENDING:
            return False
        now = now or timezone.now()
        return (
            self.starts_at <= now
            or self.application.status != JobApplication.Status.IN_PROGRESS
        )
