# backend/accounts/adapter.py

"""
Account adapter — what the authentication API says about a user
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Adjust django-allauth to this project: the name shown for a user, the role
and the demo mark added to the user data that the headless API returns to
the frontend, and the security notices that must never break the change
they tell of.
Nothing else is customised here.
"""

import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.headless.adapter import DefaultHeadlessAdapter

logger = logging.getLogger(__name__)


def display_name(user):
    """Return the name shown for a user, in the API and in the e-mails."""
    # Accounts created before the names were asked at sign-up have none:
    # their address stands in until an administrator fills them in
    return user.get_full_name() or user.email


class HeadlessAdapter(DefaultHeadlessAdapter):
    """User data returned by the API, with the role of the account and
    whether it is a demo account."""

    def serialize_user(self, user):
        """Return allauth's user data plus the role and the demo mark."""
        data = super().serialize_user(user)
        # The frontend chooses its screens from the role
        data["role"] = user.role
        # A demo account shows a band and keeps its address and password
        data["is_demo"] = user.is_demo
        return data


class AccountAdapter(DefaultAccountAdapter):
    """allauth's account adapter, with security notices that cannot fail."""

    def send_notification_mail(self, template_prefix, user, context=None, email=None):
        """Send a security notice (address changed, password changed or
        reset, address removed); a failure to send is written to the
        journal and the action goes on (decision of 28.10.2026). The notice
        is sent once the change is saved: an error here would show a failure
        for a change that happened. The e-mails an action depends on (the
        link to confirm an address, the link of a forgotten password) do not
        come through here: their failure is still shown."""
        try:
            super().send_notification_mail(template_prefix, user, context, email)
        except Exception as error:
            # The name of the notice and the account, never an address
            notice = template_prefix.rsplit("/", 1)[-1]
            logger.warning(
                "Security notice %s to user %s not sent (%s)",
                notice,
                user.pk,
                type(error).__name__,
            )
