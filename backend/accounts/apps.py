# backend/accounts/apps.py

"""
Accounts application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the accounts application: its Python path and
the title of its section in the admin site, and connect its signals when
the application is ready (signals.py). Contains no logic.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration of the accounts application."""

    name = "accounts"

    # Title of the section in the admin site. Without it, Django shows the
    # label in capitals, "ACCOUNTS", next to the "Accounts" section of
    # allauth (e-mail addresses): two sections with the same name
    verbose_name = "Users"

    def ready(self):
        # Importing the module connects its receivers
        from . import signals  # noqa: F401
