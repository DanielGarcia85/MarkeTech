# backend/accounts/adapter.py

"""
Account adapter — what the authentication API says about a user
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Adjust django-allauth to this project: the name shown for a user, and the
role and the demo mark added to the user data that the headless API returns
to the frontend.
Nothing else is customised here.
"""

from allauth.headless.adapter import DefaultHeadlessAdapter


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
