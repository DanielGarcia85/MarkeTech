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

# The application sits behind the server's reverse proxy, which ends the
# HTTPS connection and passes requests on over plain HTTP. This header,
# written by that proxy and passed on by the application's own Nginx, tells
# Django that the visitor did come over HTTPS.
# https://docs.djangoproject.com/en/6.1/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Send the session cookie and the form-protection cookie over HTTPS only
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTPS is enforced by the server's reverse proxy, before requests reach the
# application: it redirects HTTP to HTTPS and tells browsers to come back
# over HTTPS only (HSTS header). Django does neither a second time. A
# redirect would break the plain-HTTP door on port 8080, used locally and
# for tests; and Django would add the header to its own responses only, not
# to the pages of the Vue application. The two deployment checks that ask
# for these settings are therefore silenced.
SILENCED_SYSTEM_CHECKS = ["security.W004", "security.W008"]

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
