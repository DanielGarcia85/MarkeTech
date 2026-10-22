# backend/demo/apps.py

"""
Demo application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the demo application, which holds no model and
no admin section: the seed_demo command, which fills a database with test
data taken from every other application, and the public demonstration
(decisions of 22.10.2026): the login to a demo account without password
(views.py), what a demo account may not do (middleware.py), how often it
may write (throttles.py). Kept apart so that no application of the site
depends on the ones built after it. Contains no logic.
"""

from django.apps import AppConfig


class DemoConfig(AppConfig):
    """Configuration of the demo application."""

    name = "demo"
