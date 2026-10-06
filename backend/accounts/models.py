# backend/accounts/models.py

"""
Account models — the user of the platform
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Define the user model of the project. Roles and profiles are not handled
here yet.

Why a custom model
──────────────────
Django creates the user table in its very first migration, and replacing the
user model afterwards is costly. Declaring our own model from the start, even
without any change, keeps the door open for later additions.
"""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Platform user. Extends Django's default user without any change yet."""
