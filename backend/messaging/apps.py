# backend/messaging/apps.py

"""
Messaging application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the messaging application: its Python path and
the title of its section in the admin site. Contains no other logic.
"""

from django.apps import AppConfig


class MessagingConfig(AppConfig):
    """Configuration of the messaging application."""

    name = "messaging"

    # Title of the section in the admin site
    verbose_name = "Messaging"
