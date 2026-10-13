# backend/accounts/managers.py

"""
Account managers — creation and lookup of users by e-mail address
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Provide the manager of the user model: the object that creates users and
administrators, and finds a user at login. Defines no field: the fields live
in models.py.

Why a custom manager
────────────────────
Django's own manager creates a user from a username. Our users are identified
by their e-mail address only, so the creation methods are rewritten here to
take an address instead.

Letter case of addresses
────────────────────────
An address is stored in lower case, and lowered again before a lookup, so
that "Name@Example.com" and "name@example.com" are one single account.
"""

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Create users and find them by their e-mail address."""

    @classmethod
    def normalize_email(cls, email):
        """Return the address written in lower case."""
        # Django only lowers the domain; we lower the part before the @ too
        return super().normalize_email(email).lower()

    def get_by_natural_key(self, email):
        """Return the user who has this address, whatever its letter case."""
        # Called by Django at login with the address exactly as it was typed
        return self.get(email=self.normalize_email(email))

    def create_user(self, email, password=None, **extra_fields):
        """Create and save an ordinary user, with no access to the admin."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save an administrator, who holds every permission."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Without these two flags, the account could not open the admin site
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        """Build the user, hash the password and save. Used by both methods."""
        if not email:
            raise ValueError("The e-mail address must be set.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # Never store the password itself: set_password() stores its hash
        user.set_password(password)
        user.save(using=self._db)
        return user
