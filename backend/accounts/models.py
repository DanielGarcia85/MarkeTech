# backend/accounts/models.py

"""
Account models — the user of the platform
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Define the user model of the project: how a user is identified and which
role the account has. Profiles are not handled here yet, and the creation of
users lives in managers.py.

Why a custom model
──────────────────
Django's default user is identified by a username. Our users log in with
their e-mail address only, so the model keeps everything Django provides
(password, permissions, dates) and replaces the username by the address.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """Platform user, identified by an e-mail address."""

    class Role(models.TextChoices):
        """Roles an account can have. An administrator has none."""

        CANDIDATE = "candidate"
        EMPLOYER = "employer"

    # Remove the username field inherited from AbstractUser
    username = None

    # Redefined to make the address required and unique: it is the login
    email = models.EmailField("email address", unique=True)

    # Empty for an administrator, who is recognised by is_staff instead
    role = models.CharField(max_length=20, choices=Role.choices, blank=True)

    # Field Django uses as the login, in the admin site and at authentication
    USERNAME_FIELD = "email"

    # Extra fields asked by the createsuperuser command: none, the address
    # and the password are always asked
    REQUIRED_FIELDS = []

    objects = UserManager()
