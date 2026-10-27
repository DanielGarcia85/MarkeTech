# backend/appointments/views.py

"""
Appointments views — the API of the appointments
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Answer the requests about the appointments: those of one application,
read by its two participants and proposed by its employer; the answer of
the candidate; the cancellation by the employer; the appointments of the
user over a period, for the calendar; how many are news, for the side bar.
Decides who may do what and when; the shape of the data is in
serializers.py.

Routes (appointments/urls.py, under /api/)
──────────────────────────────────────────
  GET   applications/<id>/appointments/  the appointments of an application,
                                         in the order they take place
  POST  applications/<id>/appointments/  propose {starts_at, duration,
                                         place, note}: the employer, while
                                         the application is in progress
  POST  appointments/<id>/answer/        {accept, message}: the candidate,
                                         while pending
  POST  appointments/<id>/cancel/        {message}: the employer, pending, or
                                         accepted and not yet taken place
  GET   appointments/                    mine (?start=…&end=…, ISO dates or
                                         times, end excluded)
  GET   appointments/unseen/             {count, applications: {id: count}}
  GET   appointments/<id>/calendar/      the appointment as a calendar file
                                         (.ics), accepted and to come only

Who may do what
───────────────
A logged-in user, else 403. Only the two participants of an application
reach its appointments: anyone else gets 404, never 403 (the API does not
say what exists). Between them, the wrong side gets 403: only the employer
proposes and cancels, only the candidate answers. A move the state does
not allow gets 400.

Seen
────
Reading the appointments of an application, or one's appointments over a
period, marks seen those whose last change is news for the user; the
answer says which were new before (decisions of 22.10.2026).

A pending appointment left without answer after its time blocks a new
proposal (one pending per application, a rule of the database): proposing
again cancels it, in the same transaction, without notice to anyone.

A proposal and a cancellation tell the candidate, an answer tells the
employer, by e-mail (notifications/send.py, decisions of 26.10.2026).

A proposal, an answer and a cancellation send a signal to the open tabs
of both people (live/notify.py, decisions of 26.10.2026).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.translation import gettext as _
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.models import JobApplication
from live import notify as live
from notifications import send as notifications

from .ics import to_ics
from .models import Appointment
from .serializers import (
    AnswerSerializer,
    AppointmentSerializer,
    CancelSerializer,
    ProposeSerializer,
)


def mine(user):
    """The appointments of which the user is a participant."""
    return Q(application__candidate__user=user) | Q(application__offer__employer__user=user)


def news_for(user):
    """The appointments whose last change is news for the user, not seen
    yet: a proposal or a cancellation for the candidate, an answer for the
    employer."""
    for_candidate = Q(application__candidate__user=user) & Q(
        status__in=[Appointment.Status.PENDING, Appointment.Status.CANCELLED]
    )
    for_employer = Q(application__offer__employer__user=user) & Q(
        status__in=[Appointment.Status.ACCEPTED, Appointment.Status.DECLINED]
    )
    return Q(seen_at__isnull=True) & (for_candidate | for_employer)


def listed(request, appointments):
    """The appointments as JSON, those that were news marked seen: the ids
    are taken before the UPDATE, so that the page still shows them new."""
    new = set(appointments.filter(news_for(request.user)).values_list("pk", flat=True))
    rows = list(appointments)
    Appointment.objects.filter(pk__in=new).update(seen_at=timezone.now())
    context = {"request": request, "new": new}
    return AppointmentSerializer(rows, many=True, context=context).data


def loaded(queryset):
    """With what the JSON reads: the application, its offer, its company,
    its candidate."""
    return queryset.select_related(
        "application__offer__employer", "application__candidate__user"
    )


class ApplicationAppointmentsView(APIView):
    """The appointments of one application."""

    permission_classes = [permissions.IsAuthenticated]

    def application(self, request, pk):
        """The application, if the user takes part in it; 404 otherwise."""
        user = request.user
        applications = JobApplication.objects.filter(
            Q(candidate__user=user) | Q(offer__employer__user=user)
        ).select_related("offer__employer", "candidate__user")
        return get_object_or_404(applications, pk=pk)

    def get(self, request, pk):
        application = self.application(request, pk)
        return Response(listed(request, loaded(application.appointments.all())))

    def post(self, request, pk):
        """A proposal of the employer, while the application is in progress,
        one pending at a time."""
        application = self.application(request, pk)
        if application.offer.employer.user_id != request.user.pk:
            raise PermissionDenied(_("Only the employer proposes an appointment."))
        if application.status != JobApplication.Status.IN_PROGRESS:
            message = _("You can propose an appointment only while the application is in progress.")
            raise ValidationError({"non_field_errors": [message]})
        form = ProposeSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        now = timezone.now()
        with transaction.atomic():
            pending = (
                application.appointments.select_for_update()
                .filter(status=Appointment.Status.PENDING)
                .first()
            )
            if pending and pending.starts_at > now:
                message = _("This application already has a pending appointment.")
                raise ValidationError({"non_field_errors": [message]})
            if pending:
                # Left without answer after its time: the new one replaces it
                pending.status = Appointment.Status.CANCELLED
                pending.answered_at = now
                pending.seen_at = now
                pending.save(update_fields=["status", "answered_at", "seen_at"])
            proposed = Appointment.objects.create(application=application, **form.validated_data)
        proposed = loaded(Appointment.objects).get(pk=proposed.pk)
        notifications.appointment_proposed(request, proposed)
        live.news(proposed.application, live.APPOINTMENTS)
        data = AppointmentSerializer(proposed, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)


class AppointmentMoveView(APIView):
    """A move of one appointment by one of its participants: the answer of
    the candidate, the cancellation by the employer (side)."""

    permission_classes = [permissions.IsAuthenticated]
    side = ""

    def appointment(self, request, pk):
        """The appointment, if the user takes part in it (404 otherwise),
        locked until the end of the transaction, and on the right side
        (403 otherwise)."""
        appointments = loaded(Appointment.objects.filter(mine(request.user)))
        appointment = get_object_or_404(appointments.select_for_update(of=("self",)), pk=pk)
        if self.side == "candidate":
            if appointment.application.candidate.user_id != request.user.pk:
                raise PermissionDenied(_("Only the candidate answers an appointment."))
        elif appointment.application.offer.employer.user_id != request.user.pk:
            raise PermissionDenied(_("Only the employer cancels an appointment."))
        return appointment

    def answered(self, request, appointment):
        """The appointment after the move, as JSON."""
        data = AppointmentSerializer(appointment, context={"request": request}).data
        return Response(data)


class AnswerView(AppointmentMoveView):
    """The candidate accepts or declines, with a message, once."""

    side = "candidate"

    def post(self, request, pk):
        form = AnswerSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        with transaction.atomic():
            appointment = self.appointment(request, pk)
            if appointment.status != Appointment.Status.PENDING or appointment.is_expired():
                message = _("This appointment can no longer be answered.")
                raise ValidationError({"non_field_errors": [message]})
            accept = form.validated_data["accept"]
            appointment.status = (
                Appointment.Status.ACCEPTED if accept else Appointment.Status.DECLINED
            )
            appointment.response = form.validated_data["message"]
            appointment.answered_at = timezone.now()
            # News for the employer now
            appointment.seen_at = None
            appointment.save()
        notifications.appointment_answered(request, appointment)
        live.news(appointment.application, live.APPOINTMENTS)
        return self.answered(request, appointment)


class CancelView(AppointmentMoveView):
    """The employer cancels a pending appointment, or an accepted one that
    has not taken place, with a word or not."""

    side = "employer"

    def post(self, request, pk):
        form = CancelSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        now = timezone.now()
        with transaction.atomic():
            appointment = self.appointment(request, pk)
            pending = appointment.status == Appointment.Status.PENDING
            accepted = appointment.status == Appointment.Status.ACCEPTED
            coming = accepted and appointment.starts_at > now
            if not (pending or coming):
                message = _("This appointment can no longer be cancelled.")
                raise ValidationError({"non_field_errors": [message]})
            appointment.status = Appointment.Status.CANCELLED
            appointment.response = form.validated_data["message"]
            appointment.answered_at = now
            # News for the candidate now
            appointment.seen_at = None
            appointment.save()
        notifications.appointment_cancelled(request, appointment)
        live.news(appointment.application, live.APPOINTMENTS)
        return self.answered(request, appointment)


def moment(value, name):
    """A date ("2026-10-22", midnight in the time zone of the server) or a
    time with its offset, from the query string; 400 if neither."""
    when = parse_datetime(value)
    if when is None:
        day = parse_date(value)
        if day is None:
            raise ValidationError({name: [_("Give a date or a time.")]})
        when = datetime(day.year, day.month, day.day)
    if timezone.is_naive(when):
        when = timezone.make_aware(when)
    return when


class MyAppointmentsView(APIView):
    """The appointments of the user, in the order they take place: all of
    them, or those that start within a period (the weeks or the month the
    calendar shows)."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        appointments = loaded(Appointment.objects.filter(mine(request.user)))
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if start:
            appointments = appointments.filter(starts_at__gte=moment(start, "start"))
        if end:
            appointments = appointments.filter(starts_at__lt=moment(end, "end"))
        return Response(listed(request, appointments))


class UnseenView(APIView):
    """How many appointments are news for the user, in all and by
    application: the side bar shows the total, the cards of the
    applications their own."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rows = (
            Appointment.objects.filter(news_for(request.user))
            .order_by()
            .values("application")
            .annotate(count=Count("pk"))
        )
        applications = {str(row["application"]): row["count"] for row in rows}
        return Response({"count": sum(applications.values()), "applications": applications})


# The day in the name of a calendar file: the day in Geneva, where the
# site is used (the database keeps UTC)
GENEVA = ZoneInfo("Europe/Zurich")


class CalendarView(APIView):
    """An accepted appointment still to come, as a calendar file to open in
    one's agenda (decisions of 22.10.2026). Any other appointment, or one
    the user takes no part in: 404."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        appointments = loaded(Appointment.objects.filter(mine(request.user))).filter(
            status=Appointment.Status.ACCEPTED, starts_at__gt=timezone.now()
        )
        appointment = get_object_or_404(appointments, pk=pk)
        application = appointment.application
        if application.candidate.user_id == request.user.pk:
            other = application.offer.employer.company_name
        else:
            person = application.candidate.user
            other = person.get_full_name() or person.email
        title = f"{application.offer.title} · {other}"
        domain = request.get_host().split(":")[0]
        response = HttpResponse(
            to_ics(appointment, title, domain), content_type="text/calendar; charset=utf-8"
        )
        day = timezone.localtime(appointment.starts_at, GENEVA).date().isoformat()
        response["Content-Disposition"] = f'attachment; filename="rendez-vous-{day}.ics"'
        return response
