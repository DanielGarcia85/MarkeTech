# backend/reviews/apps.py

"""
Reviews application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the reviews application: its Python path and
the title of its section in the admin site. Contains no other logic.
"""

from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Configuration of the reviews application."""

    name = "reviews"

    # Title of the section in the admin site
    verbose_name = "Reviews"
