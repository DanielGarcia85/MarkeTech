# backend/notifications/send.py

"""
Notifications — the e-mails that tell a user what happened on the site
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Write and send the e-mail of an event to the user it concerns (decisions
of 26.10.2026): a new application and a withdrawal to the employer, a move
of the state to the candidate, a new message to the other participant, an
appointment proposed or cancelled to the candidate, accepted or declined to
the employer. Called by the views, after the change is made. One function
per event; each gives the user, the page to open and what the e-mail says.

The rules
─────────
- Nobody gets an e-mail they do not want: not a user who turned the
  notifications off (notify_by_email), not a demo account, not an address
  in example.com (the accounts of the seed, which receive nothing), not an
  account the administrator blocked.
- The e-mail goes in the language of the user (accounts/signals.py), the
  language of the site while it is unknown.
- It says who, what and about which offer, with the link to the page; never
  the text of a message nor of an answer: one logs in to read them.
- It leaves once the change is in the database (transaction.on_commit):
  never for a change that was rolled back.
- A failure to send never breaks the action of the user: it is caught and
  written to the journal with the event and the number of the account,
  never the address (the journal holds no e-mail address).

The templates
─────────────
backend/templates/notifications/<event>_subject.txt and
<event>_message.txt, both languages in each file, as the e-mails of
allauth (backend/templates/account/email/).
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import translation

logger = logging.getLogger(__name__)

# The pages the e-mails lead to, in the frontend (router.ts)
CREDENTIALS = "/account/credentials"
CANDIDATE_APPLICATIONS = "/candidate/applications"


def wants(user):
    """Whether the user receives the notifications."""
    return (
        user.is_active
        and user.notify_by_email
        and not user.is_demo
        and not user.email.lower().endswith("@example.com")
    )


def notify(request, user, event, path, **context):
    """Send the e-mail of an event to a user, once the change is saved.
    path is the page of the frontend to open; the links are made absolute
    from the request (the domain of the site, https behind the proxy)."""
    if not wants(user):
        return
    context = {
        "user": user,
        "url": request.build_absolute_uri(path),
        "settings_url": request.build_absolute_uri(CREDENTIALS),
        **context,
    }
    language = user.language or settings.LANGUAGE_CODE
    address = user.email

    def send():
        try:
            with translation.override(language):
                subject = render_to_string(f"notifications/{event}_subject.txt", context)
                body = render_to_string(f"notifications/{event}_message.txt", context)
            # A subject is one line; the body starts with its greeting (the
            # comments of the templates leave empty lines)
            subject = " ".join(subject.split())
            send_mail(subject, body.strip() + "\n", None, [address])
        except Exception as error:
            logger.warning(
                "Notification %s to user %s not sent (%s)", event, user.pk, type(error).__name__
            )

    transaction.on_commit(send)


# ── Who is who ────────────────────────────────────────────────────────


def candidate_name(application):
    """The name of the candidate, as the employer reads it."""
    person = application.candidate.user
    return person.get_full_name() or person.email


def company_name(application):
    """The name of the company, as the candidate reads it."""
    return application.offer.employer.company_name


def conversation(application):
    """The page of the conversation of an application."""
    return f"/messages/{application.pk}"


def received(application):
    """The applications received for the offer of an application."""
    return f"/employer/applications?offer={application.offer_id}"


# ── The applications ──────────────────────────────────────────────────


def application_received(request, application):
    """A candidate applied: the employer of the offer is told."""
    notify(
        request,
        application.offer.employer.user,
        "application_received",
        received(application),
        candidate=candidate_name(application),
        offer=application.offer.title,
    )


def application_withdrawn(request, application):
    """A candidate withdrew their application: the employer is told. Called
    before the application is deleted, which the e-mail then follows."""
    notify(
        request,
        application.offer.employer.user,
        "application_withdrawn",
        received(application),
        candidate=candidate_name(application),
        offer=application.offer.title,
    )


def application_moved(request, application, with_message):
    """The employer moved the state: the candidate is told, and whether a
    message came with it (one e-mail, not two)."""
    notify(
        request,
        application.candidate.user,
        "application_moved",
        conversation(application) if with_message else CANDIDATE_APPLICATIONS,
        company=company_name(application),
        offer=application.offer.title,
        status=application.status,
        with_message=with_message,
    )


# ── The messages ──────────────────────────────────────────────────────


def message_written(request, message):
    """A new message: the other participant is told, only when it is the
    first they have not read in this conversation (one e-mail until they
    read, not one per message)."""
    application = message.application
    employer = application.offer.employer.user
    candidate = application.candidate.user
    recipient = candidate if message.author_id == employer.pk else employer
    unread = application.messages.filter(read_at__isnull=True).exclude(author=recipient)
    if unread.count() != 1:
        return
    sender = company_name(application) if recipient == candidate else candidate_name(application)
    notify(
        request,
        recipient,
        "message_written",
        conversation(application),
        sender=sender,
        offer=application.offer.title,
    )


# ── The appointments ──────────────────────────────────────────────────


def appointment_context(appointment):
    """What the e-mails of an appointment say of it."""
    application = appointment.application
    return {
        "company": company_name(application),
        "candidate": candidate_name(application),
        "offer": application.offer.title,
        "starts_at": appointment.starts_at,
        "duration": appointment.duration,
    }


def appointment_proposed(request, appointment):
    """The employer proposed an appointment: the candidate is told."""
    notify(
        request,
        appointment.application.candidate.user,
        "appointment_proposed",
        conversation(appointment.application),
        **appointment_context(appointment),
    )


def appointment_answered(request, appointment):
    """The candidate accepted or declined: the employer is told."""
    notify(
        request,
        appointment.application.offer.employer.user,
        "appointment_answered",
        conversation(appointment.application),
        accepted=appointment.status == "accepted",
        **appointment_context(appointment),
    )


def appointment_cancelled(request, appointment):
    """The employer cancelled: the candidate is told."""
    notify(
        request,
        appointment.application.candidate.user,
        "appointment_cancelled",
        conversation(appointment.application),
        **appointment_context(appointment),
    )
