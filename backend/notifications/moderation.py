# backend/notifications/moderation.py

"""
Moderation alerts — the e-mails that tell the administrator what became public
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Tell the administrator, by e-mail, of every content that is public as soon
as it is written (decisions of 26.10.2026): a review written or rewritten,
an offer published or changed while it is published. The moderation is
done after the fact: the content is online at once, the e-mail gives the
text and the link to its page in the admin, where the administrator
deletes it or blocks the account (is_active), which takes all its content
out of sight. Called by the views of the reviews and of the offers.

The rules
─────────
- The e-mail goes to MODERATION_EMAIL (settings), in French: it is read by
  the administrator only. No alert when the setting is empty.
- It carries the whole text, the author and their address: everything
  needed to judge without logging in. The journal never does.
- Nothing for a demo account: its content is reset every night.
- It leaves once the change is in the database (transaction.on_commit), and
  a failure to send never breaks the action of the user: it is written to
  the journal with the event, never an address.

The templates
─────────────
backend/templates/moderation/<event>_subject.txt and <event>_message.txt.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation

logger = logging.getLogger(__name__)


def alert(request, author, event, admin_path, **context):
    """Send the alert of an event to the administrator, once the change is
    saved. admin_path is the page of the content in the admin; the links
    are made absolute from the request."""
    if not settings.MODERATION_EMAIL or author.is_demo:
        return
    context = {
        "author": author,
        "admin_url": request.build_absolute_uri(admin_path),
        "account_url": request.build_absolute_uri(
            reverse("admin:accounts_user_change", args=[author.pk])
        ),
        **context,
    }

    def send():
        try:
            with translation.override("fr"):
                subject = render_to_string(f"moderation/{event}_subject.txt", context)
                body = render_to_string(f"moderation/{event}_message.txt", context)
            send_mail(" ".join(subject.split()), body.strip() + "\n", None, [settings.MODERATION_EMAIL])
        except Exception as error:
            logger.warning("Moderation alert %s not sent (%s)", event, type(error).__name__)

    transaction.on_commit(send)


def review_written(request, review, created):
    """A review written (created) or rewritten: public on the page of the
    reviews and in the side bar."""
    alert(
        request,
        review.user,
        "review_written",
        reverse("admin:reviews_review_change", args=[review.pk]),
        review=review,
        created=created,
        page_url=request.build_absolute_uri("/reviews"),
    )


def offer_published(request, offer, changed):
    """An offer published, or changed while it is published (changed):
    public in the list and on its page."""
    alert(
        request,
        offer.employer.user,
        "offer_published",
        reverse("admin:offers_joboffer_change", args=[offer.pk]),
        offer=offer,
        changed=changed,
        page_url=request.build_absolute_uri(f"/offers/{offer.pk}"),
    )
