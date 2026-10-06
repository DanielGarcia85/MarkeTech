# backend/config/settings/base.py

"""
Base settings — configuration shared by every environment
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Declare the settings common to every environment: installed applications,
middleware chain, templates, password rules, internationalisation, static
files and email. Contains no secret and nothing specific to one environment:
debug mode, allowed hosts and the database are set in the environment files,
such as dev.py.

References
──────────
  - https://docs.djangoproject.com/en/6.1/topics/settings/
  - https://docs.djangoproject.com/en/6.1/ref/settings/
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ── Paths and environment ─────────────────────────────────────────────

# Folder that contains manage.py (backend/). Build other paths from it, for
# example BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load the variables of the root .env file into the environment. When the
# file does not exist, the call does nothing and the variables must already
# be defined in the environment.
load_dotenv(BASE_DIR.parent / ".env")

# ── Security ──────────────────────────────────────────────────────────

# Read from the environment, with no fallback value: a missing key must stop
# the application at startup.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# ── Applications ──────────────────────────────────────────────────────

INSTALLED_APPS = [
    # Administration interface
    "django.contrib.admin",
    # Users, groups and permissions
    "django.contrib.auth",
    # Registry of models, used by the permission system
    "django.contrib.contenttypes",
    # Server-side sessions
    "django.contrib.sessions",
    # One-off notifications (unrelated to the future messaging feature)
    "django.contrib.messages",
    # Management of static files
    "django.contrib.staticfiles",
    # Third-party applications
    "rest_framework",
    # Project applications
    "accounts",
]

# Model used for every user account, instead of Django's default one. Must be
# set before the first migration is created.
AUTH_USER_MODEL = "accounts.User"

# ── Middleware ────────────────────────────────────────────────────────

# Each request goes through this chain from top to bottom, and the response
# travels back from bottom to top. The order matters.
MIDDLEWARE = [
    # Security headers and HTTPS redirection
    "django.middleware.security.SecurityMiddleware",
    # Loads the session identified by the cookie
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Normalises URLs, for example by appending a missing trailing slash
    "django.middleware.common.CommonMiddleware",
    # CSRF protection
    "django.middleware.csrf.CsrfViewMiddleware",
    # Attaches the logged-in user to the request
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Handles one-off notifications
    "django.contrib.messages.middleware.MessageMiddleware",
    # Forbids displaying the site inside a frame on another site
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ── Routing, templates and entry point ────────────────────────────────

# Module that holds the root URL table
ROOT_URLCONF = "config.urls"

# HTML template engine, used by the administration interface
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Entry point used by the development server
WSGI_APPLICATION = "config.wsgi.application"

# ── Password validation ───────────────────────────────────────────────

# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators
# The class paths below are longer than the usual line limit and are kept on
# one line for readability.
AUTH_PASSWORD_VALIDATORS = [
    {
        # Rejects a password too similar to the user's own attributes
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        # Requires a minimum length
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        # Rejects commonly used passwords
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        # Rejects a password made of digits only
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ── Internationalisation ──────────────────────────────────────────────

# https://docs.djangoproject.com/en/6.1/topics/i18n/
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

# Enables Django's translation system
USE_I18N = True

# Stores dates and times in UTC, with time zone information
USE_TZ = True

# ── Static files ──────────────────────────────────────────────────────

# https://docs.djangoproject.com/en/6.1/howto/static-files/
# URL prefix of static files (CSS, JavaScript, images)
STATIC_URL = "static/"

# ── REST API ──────────────────────────────────────────────────────────

# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    # Identify the user from the Django session cookie
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Deny by default: every view requires a logged-in user, unless it
    # explicitly declares another permission
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# ── Email ─────────────────────────────────────────────────────────────

# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration
# The console backend prints emails in the terminal instead of sending them.
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}
