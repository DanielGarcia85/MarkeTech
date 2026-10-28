# backend/config/settings/prod.py

"""
Production settings — configuration of the deployed application
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Complete the base settings for an environment exposed to real users: debug
mode off, allowed hosts, PostgreSQL database, a channel layer on Redis,
optimised static files and real e-mail sending.
Every value that differs from one deployment to another is read from the
environment, with no fallback value: a missing variable must stop the
application at startup.

References
──────────
  - https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/
  - https://docs.djangoproject.com/en/6.1/ref/settings/#databases
  - https://whitenoise.readthedocs.io/en/stable/django.html
  - https://docs.djangoproject.com/en/6.1/topics/email/#smtp-backend
  - https://channels.readthedocs.io/en/stable/topics/channel_layers.html
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

# ── Real time ─────────────────────────────────────────────────────────

# The channel layer on Redis (decision of 26.10.2026), shared by every
# process of the backend. The address names the redis service of
# docker-compose.yml, as in redis://redis:6379/0; it is set there, like
# POSTGRES_HOST
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": os.environ["REDIS_URL"],
                    # A tab waits for its signals in Redis 5 seconds at a time
                    # (brpop_timeout of channels-redis), and the client of
                    # redis 8 gives up a reading after 5 seconds by default:
                    # the tab's connection would be cut every 5 seconds
                    "socket_timeout": 10,
                }
            ]
        },
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

# ── Email ─────────────────────────────────────────────────────────────

# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration
# Real sending, through the outgoing mail server of the provider, with the
# login of the mailbox that sends. The connection is encrypted (STARTTLS).
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": os.environ["EMAIL_HOST"],
            "port": int(os.environ["EMAIL_PORT"]),
            "username": os.environ["EMAIL_HOST_USER"],
            "password": os.environ["EMAIL_HOST_PASSWORD"],
            "use_tls": True,
        },
    },
}

# Sender of the application's e-mails
DEFAULT_FROM_EMAIL = os.environ["DEFAULT_FROM_EMAIL"]
