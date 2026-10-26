# backend/accounts/admin.py

"""
Accounts administration — users in the Django admin site
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Register the user model in the administration interface, with the screens
Django provides for users: list, search and password change form.

Why the screens are redefined
─────────────────────────────
Django's ready-made configuration names the username field in every screen.
Our model has none, so each list of fields is written again here, with the
e-mail address in its place and the role added.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """User screens of the admin site, built on the e-mail address."""

    # Screen that edits an existing user
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role", "is_demo")}),
        ("Notifications", {"fields": ("language", "notify_by_email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined", "terms_accepted_at")}),
    )

    # Set by the sign-up form only: shown, never edited by hand
    readonly_fields = ("terms_accepted_at",)

    # Screen that creates a user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "usable_password",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # List of users: every field of the model except the password hash
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_demo",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
        "date_joined",
    )
    # Both id and e-mail open the user's page, not only the first column
    list_display_links = ("id", "email")
    list_filter = ("role", "is_demo", "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    date_hierarchy = "date_joined"
