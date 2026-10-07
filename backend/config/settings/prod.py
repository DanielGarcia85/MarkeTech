# backend/config/settings/prod.py

"""
Production settings — configuration of the deployed application
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Complete the base settings for an environment exposed to real users: debug
mode off, allowed hosts, PostgreSQL database and optimised static files.
Every value that differs from one deployment to another is read from the
environment, with no fallback value: a missing variable must stop the
application at startup.

References
──────────
  - https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/
  - https://docs.djangoproject.com/en/6.1/ref/settings/#databases
  - https://whitenoise.readthedocs.io/en/stable/django.html
"""

import os

from .base import *

# ── Security ──────────────────────────────────────────────────────────

# Never show detailed error pages to visitors
DEBUG = False

# Host names the application agrees to answer for, separated by commas and
# without spaces
ALLOWED_HOSTS = os.environ["DJANGO_ALLOWED_HOSTS"].split(",")

# ── Database ──────────────────────────────────────────────────────────

# https://docs.djangoproject.com/en/6.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        # Name of the machine that runs PostgreSQL. The port is the default
        # one, 5432.
        "HOST": os.environ["POSTGRES_HOST"],
    }
}

# ── Static files ──────────────────────────────────────────────────────

# https://docs.djangoproject.com/en/6.1/ref/settings/#storages
STORAGES = {
    # Files uploaded by users: Django's default storage, unchanged
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    # Static files: compressed, and renamed with a fingerprint of their
    # content so that browsers can keep them in cache for a long time
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
