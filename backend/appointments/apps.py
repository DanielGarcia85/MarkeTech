# backend/appointments/apps.py

"""
Appointments application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the appointments application: its Python path
and the title of its section in the admin site. Contains no other logic.
"""

from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    """Configuration of the appointments application."""

    name = "appointments"

    # Title of the section in the admin site
    verbose_name = "Appointments"
