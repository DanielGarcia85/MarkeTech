# backend/demo/apps.py

"""
Demo application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the demo application, which holds no model, no
view and no admin section: only the seed_demo command, which fills a
development database with test data taken from every other application.
Kept apart so that no application of the site depends on the ones built
after it. Contains no logic.
"""

from django.apps import AppConfig


class DemoConfig(AppConfig):
    """Configuration of the demo application."""

    name = "demo"
