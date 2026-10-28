# backend/live/apps.py

"""
Live application — declaration of the application to Django
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give Django the identity of the live application: its Python path. It
holds the real time of the site (decisions of 26.10.2026): the consumer
that keeps the WebSocket of a logged-in user open (consumers.py), the
route /ws/ (routing.py), and the signals the views send to it
(notify.py). It has no model and no table. Contains no logic.
"""

from django.apps import AppConfig


class LiveConfig(AppConfig):
    """Configuration of the live application."""

    name = "live"
