# backend/notifications/apps.py

"""
Notifications application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the notifications application: its Python
path. It has no model and no route: the views of the other applications
call send.py. Contains no logic.
"""

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Configuration of the notifications application."""

    name = "notifications"
