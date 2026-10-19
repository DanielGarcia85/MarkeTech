# backend/profiles/apps.py

"""
Profiles application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the profiles application: its Python path and
the title of its section in the admin site, and connect its signals once
the models are loaded. Contains no other logic.
"""

from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    """Configuration of the profiles application."""

    name = "profiles"

    # Title of the section in the admin site
    verbose_name = "Profiles"

    def ready(self):
        """Called by Django once every model is loaded."""
        # Imported for its effect only: the module registers the receivers
        # that delete the files of a deleted record (signals.py)
        from . import signals  # noqa: F401
