# backend/accounts/models.py

"""
Account models — the user of the platform
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Define the user model of the project: how a user is identified, which
role the account has, and how it hears of what happens (the language of
its e-mails, whether it receives the notifications). Profiles are not handled here yet, and the creation of
users lives in managers.py.

Why a custom model
──────────────────
Django's default user is identified by a username. Our users log in with
their e-mail address only, so the model keeps everything Django provides
(password, permissions, dates) and replaces the username by the address.
"""

from django.conf import settings
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

    # When the user accepted the terms of use at sign-up (forms.py); empty
    # for an account created before the terms existed, or in the admin site
    terms_accepted_at = models.DateTimeField(null=True, blank=True)

    # An account of the public demonstration, made by seed_demo: anyone may
    # open it with a button of the login page (demo/views.py), it cannot
    # change its address nor its password (demo/middleware.py), and it is
    # made again every night (decisions of 22.10.2026)
    is_demo = models.BooleanField(default=False)

    # The language of the e-mails the user receives without asking for them
    # (the notifications): the language of the interface at their last login
    # or change of language (decisions of 26.10.2026). Empty until then: the
    # e-mails go in the language of the site, LANGUAGE_CODE
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, blank=True)

    # Whether the user receives the notifications by e-mail (a new
    # application, a move, a message, an appointment); the e-mails of the
    # account itself (verification, password) always go
    notify_by_email = models.BooleanField(default=True)

    # Field Django uses as the login, in the admin site and at authentication
    USERNAME_FIELD = "email"

    # Extra fields asked by the createsuperuser command: none, the address
    # and the password are always asked
    REQUIRED_FIELDS = []

    objects = UserManager()
