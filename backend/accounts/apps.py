# backend/accounts/apps.py

"""
Accounts application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the accounts application: its Python path and its
label. Contains no logic.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration of the accounts application."""

    name = "accounts"
