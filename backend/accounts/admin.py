# backend/accounts/admin.py

"""
Accounts administration — users in the Django admin site
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Register the user model in the administration interface, with the screens
Django provides for users: list, search and password change form.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

# UserAdmin is Django's ready-made configuration for user screens
admin.site.register(User, UserAdmin)
