# backend/applications/apps.py

"""
Applications application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the job applications application: its Python
path, the title of its section in the admin site, and connect its signals
once the models are loaded. Contains no other logic.
"""

from django.apps import AppConfig


class ApplicationsConfig(AppConfig):
    """Configuration of the job applications application."""

    name = "applications"

    # Title of the section in the admin site
    verbose_name = "Job applications"

    def ready(self):
        """Called by Django once every model is loaded."""
        # Imported for its effect only: the module registers the receivers
        # that delete the files of a deleted record (signals.py)
        from . import signals  # noqa: F401
