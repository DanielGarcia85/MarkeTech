# backend/accounts/adapter.py

"""
Account adapter — what the authentication API says about a user
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Adjust django-allauth to this project: add the role to the user data that the
headless API returns to the frontend. Nothing else is customised here.
"""

from allauth.headless.adapter import DefaultHeadlessAdapter


class HeadlessAdapter(DefaultHeadlessAdapter):
    """User data returned by the API, with the role of the account."""

    def serialize_user(self, user):
        """Return allauth's user data plus the role."""
        data = super().serialize_user(user)
        # The frontend chooses its screens from the role
        data["role"] = user.role
        return data
