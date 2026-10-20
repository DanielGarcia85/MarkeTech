# backend/offers/apps.py

"""
Offers application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the offers application: its Python path and the
title of its section in the admin site. Contains no other logic.
"""

from django.apps import AppConfig


class OffersConfig(AppConfig):
    """Configuration of the offers application."""

    name = "offers"

    # Title of the section in the admin site
    verbose_name = "Job offers"
