# backend/appointments/serializers.py

"""
Appointments serializers — the JSON shape of the appointments
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Turn an appointment into JSON for the pages: when, how long, where, what
the employer adds, its state as the pages show it ("expired" included, a
state computed and never stored), the answer, whether it is news for the
user asking, and what it is about (the application, the offer, the
company, the other participant), so that the calendar shows it without
another request. Check what a participant sends: a proposal, an answer, a
cancellation. Who may do what is decided by the views.
"""

from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import MAX_LENGTH, Appointment

# How far ahead an appointment may be proposed
FURTHEST = timedelta(days=365)

# The same sentence as for a message: DRF puts the length in its place
TOO_LONG = _("A message has at most {max_length} characters.")


def role_in(appointment, user):
    """"candidate" or "employer": the side of the user in the appointment."""
    if appointment.application.candidate.user_id == user.pk:
        return "candidate"
    return "employer"


class AppointmentSerializer(serializers.ModelSerializer):
    """An appointment as the conversation and the calendar show it. Reads
    the application, its offer, its company and its candidate: the views
    load them with the appointments (select_related)."""

    ends_at = serializers.DateTimeField(read_only=True)
    state = serializers.SerializerMethodField()
    new = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "application",
            "starts_at",
            "ends_at",
            "duration",
            "place",
            "note",
            "state",
            "response",
            "answered_at",
            "created_at",
            "new",
            "about",
        ]
        read_only_fields = fields

    def get_state(self, appointment):
        """The state stored, or "expired" for a pending one that can no
        longer be answered."""
        return "expired" if appointment.is_expired() else appointment.status

    def get_new(self, appointment):
        """Its last change is news for the user asking, not seen yet. The
        views compute it before they mark the appointments seen, and pass
        the ids in the context."""
        return appointment.pk in self.context.get("new", ())

    def get_about(self, appointment):
        """The offer, its company and the other participant: the company for
        the candidate, the candidate for the employer."""
        application = appointment.application
        company = application.offer.employer
        if role_in(appointment, self.context["request"].user) == "candidate":
            other = company.company_name
        else:
            person = application.candidate.user
            other = person.get_full_name() or person.email
        return {
            "offer": application.offer.title,
            "company": company.company_name,
            "other": other,
        }


class ProposeSerializer(serializers.Serializer):
    """What the employer proposes: a time in the future, within a year, one
    of the lengths offered, a place, and a note if they wish."""

    starts_at = serializers.DateTimeField(
        error_messages={"invalid": _("Give a date and a time."), "required": _("Give a date and a time.")}
    )
    duration = serializers.ChoiceField(
        choices=Appointment.Duration.choices,
        default=Appointment.Duration.HOUR,
        error_messages={"invalid_choice": _("This length is not offered.")},
    )
    place = serializers.CharField(
        max_length=200,
        trim_whitespace=True,
        error_messages={
            "blank": _("Say where, or how, you will meet."),
            "required": _("Say where, or how, you will meet."),
            "max_length": _("A place has at most {max_length} characters."),
        },
    )
    note = serializers.CharField(
        max_length=MAX_LENGTH,
        trim_whitespace=True,
        allow_blank=True,
        default="",
        error_messages={"max_length": TOO_LONG},
    )

    def validate_starts_at(self, value):
        now = timezone.now()
        if value <= now:
            raise serializers.ValidationError(_("An appointment is proposed in the future."))
        if value > now + FURTHEST:
            raise serializers.ValidationError(_("An appointment is proposed within a year."))
        return value


class AnswerSerializer(serializers.Serializer):
    """The answer of the candidate: accept or decline, with a message."""

    accept = serializers.BooleanField(
        error_messages={"required": _("Accept or decline the appointment.")}
    )
    message = serializers.CharField(
        max_length=MAX_LENGTH,
        trim_whitespace=True,
        error_messages={
            "blank": _("Write a message with your answer."),
            "required": _("Write a message with your answer."),
            "max_length": TOO_LONG,
        },
    )


class CancelSerializer(serializers.Serializer):
    """The word of the employer cancelling, if they wish."""

    message = serializers.CharField(
        max_length=MAX_LENGTH,
        trim_whitespace=True,
        allow_blank=True,
        default="",
        error_messages={"max_length": TOO_LONG},
    )
