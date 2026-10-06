# backend/config/settings/dev.py

"""
Development settings — configuration of a developer workstation
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Extend the base settings with what only applies on a local machine: debug
mode, local host names and a SQLite database stored in a file. Must never be
used on a server.
"""

from .base import *

# ── Security ──────────────────────────────────────────────────────────

# Detailed error pages, for development only
DEBUG = True

# Host names this site is allowed to serve
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# ── Database ──────────────────────────────────────────────────────────

# https://docs.djangoproject.com/en/6.1/ref/settings/#databases
# SQLite needs no server: the whole database is the db.sqlite3 file
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
