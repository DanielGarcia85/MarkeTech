# backend/live/notify.py

"""
Live signals — telling the open tabs that something changed
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Send the signal of an event to the open tabs of the two people of an
application, the candidate and the employer (decisions of 26.10.2026):
something new in its messages, in its state, or in its appointments.
Called by the views, after the change is made. The signal goes into the
channel layer, to the group of each person (consumers.py), and the
consumer of each open tab passes it on to the browser, which reads again
through the API.

The rules
─────────
- Both people get it, the one who acted included: their other tabs and
  devices follow; the tab that acted reads once more, at no harm.
- A signal says the kind and the application, never the data.
- It leaves once the change is in the database (transaction.on_commit):
  never for a change that was rolled back, and never before the page could
  read it.
- A failure to send never breaks the action of the user: it is written to
  the journal with the kind and the number of the account.
- Nothing to do with the e-mails: a signal reaches only a tab that is open,
  whatever the notifications box says.
"""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

from .consumers import group_of

logger = logging.getLogger(__name__)

# The kinds of news, as the browser reads them (live.ts)
MESSAGES = "messages"
APPLICATIONS = "applications"
APPOINTMENTS = "appointments"


def news(application, kind):
    """Tell the open tabs of the candidate and of the employer of an
    application that something of this kind changed in it."""
    # Read now: the application may be deleted (a withdrawal) before the
    # signal leaves
    application_id = application.pk
    people = (application.candidate.user_id, application.offer.employer.user_id)

    def send():
        layer = get_channel_layer()
        for user_id in people:
            try:
                async_to_sync(layer.group_send)(
                    group_of(user_id),
                    {"type": "news", "kind": kind, "application": application_id},
                )
            except Exception as error:
                logger.warning(
                    "Live signal %s to user %s not sent (%s)", kind, user_id, type(error).__name__
                )

    transaction.on_commit(send)
