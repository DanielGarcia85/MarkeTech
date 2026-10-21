# backend/favorites/apps.py

"""
Favorites application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the favorites application: its Python path and
the title of its section in the admin site. Contains no other logic.
"""

from django.apps import AppConfig


class FavoritesConfig(AppConfig):
    """Configuration of the favorites application."""

    name = "favorites"

    # Title of the section in the admin site
    verbose_name = "Favorites"
