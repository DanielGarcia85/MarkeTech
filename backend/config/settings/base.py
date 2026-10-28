# backend/config/settings/base.py

"""
Base settings — configuration shared by every environment
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Declare the settings common to every environment: installed applications,
middleware chain, authentication, templates, password rules,
internationalisation, static files and email. Contains no secret and nothing
specific to one environment: debug mode, allowed hosts and the database are
set in the environment files, such as dev.py.

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
    # Daphne first: its runserver command replaces Django's, so that the
    # development server speaks ASGI and accepts the WebSockets, like the
    # server in production
    "daphne",
    # Administration interface
    "django.contrib.admin",
    # Users, groups and permissions
    "django.contrib.auth",
    # Registry of models, used by the permission system
    "django.contrib.contenttypes",
    # Server-side sessions
    "django.contrib.sessions",
    # One-off notices of the admin site (unrelated to the messaging between
    # candidates and employers)
    "django.contrib.messages",
    # Management of static files
    "django.contrib.staticfiles",
    # Third-party applications
    "rest_framework",
    # Accounts: sign-up, login, e-mail verification, password reset
    "allauth",
    "allauth.account",
    # Same features exposed as a JSON API for the Vue frontend
    "allauth.headless",
    # Countries: ISO 3166-1 codes with their names in every language
    "django_countries",
    # Project applications
    "accounts",
    # Profiles: what a candidate or an employer says about themselves
    "profiles",
    # Offers: the job offers of the employers
    "offers",
    # Applications: the candidates applying to the offers
    "applications",
    # Favorites: the offers a candidate puts aside
    "favorites",
    # Messaging: the messages between a candidate and an employer on an application
    "messaging",
    # Appointments: the meetings an employer proposes about an application
    "appointments",
    # Reviews: what the users think of the platform, public
    "reviews",
    # Notifications: the e-mails that tell a user what happened, no model
    "notifications",
    # Live: the WebSocket of a logged-in user and the signals sent to it
    "live",
    # Demo: the public demo accounts (login, guard, write limits) and the
    # seed_demo command that fills them
    "demo",
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
    # Serves static files itself, before the request reaches the views
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Loads the session identified by the cookie
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Picks the language of the request (Accept-Language header)
    "django.middleware.locale.LocaleMiddleware",
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
    # Required by allauth: gives it access to the current request
    "allauth.account.middleware.AccountMiddleware",
    # Refuses the changes of address and password to a demo account
    "demo.middleware.DemoGuardMiddleware",
]

# ── Authentication ────────────────────────────────────────────────────

# Both backends check the password: Django's one serves the admin site,
# allauth's one serves the sign-up and login API
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# https://docs.allauth.org/en/latest/account/configuration.html
# The user model has no username: the e-mail address is the only identifier
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_LOGIN_METHODS = {"email"}
# Name shown for a user, in the API and in the e-mails: first and last name,
# or the address while they are unknown
ACCOUNT_USER_DISPLAY = "accounts.adapter.display_name"
# Fields of the sign-up form; the star marks a required field. The API
# receives the password under the name "password"; asking for it twice is
# the frontend's job. The names and the role are added by
# ACCOUNT_SIGNUP_FORM_CLASS below.
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*"]
ACCOUNT_SIGNUP_FORM_CLASS = "accounts.forms.SignupForm"
# A new account cannot log in before its address is verified by the link
# sent by e-mail
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# One address per account. To change it, the user gives the new one, which
# receives a confirmation link; the current address stays in force until the
# link is opened, then the new one replaces it
ACCOUNT_CHANGE_EMAIL = True
# Start of the subject of every e-mail sent by allauth: none, the sender
# already shows "MarkeTech" (decision of 26.10.2026; "[MarkeTech] " before).
# An empty text, not None: None would make allauth add the name of the site
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
# Security notices: an e-mail after every change to the account (address
# changed, sent to the old one; password changed or reset; address removed),
# with the IP address, the browser and the time (decision of 28.10.2026).
# Texts in templates/account/email/, frame base_notification.txt
ACCOUNT_EMAIL_NOTIFICATIONS = True

# https://docs.allauth.org/en/latest/headless/configuration.html
# No HTML page from allauth: the Vue frontend renders everything
HEADLESS_ONLY = True
# The frontend runs in the browser, on the same domain, with the session
# cookie: no token-based client
HEADLESS_CLIENTS = ("browser",)
# Adds the role to the user data returned by the API
HEADLESS_ADAPTER = "accounts.adapter.HeadlessAdapter"
# Pages of the frontend that the e-mails sent by allauth point to. The
# {key} placeholder is replaced by the one-time key of the link.
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": "/account/verify-email/{key}",
    "account_reset_password": "/account/password/reset",
    "account_reset_password_from_key": "/account/password/reset/{key}",
    "account_signup": "/account/signup",
}

# ── Routing, templates and entry point ────────────────────────────────

# Module that holds the root URL table
ROOT_URLCONF = "config.urls"

# Template engine, used by the administration interface and the e-mails
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Searched before the applications: our files replace those of allauth
        "DIRS": [BASE_DIR / "templates"],
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

# Entry points of the application for a server. ASGI is the one MarkeTech
# uses, in production (Daphne) and in development (runserver, given by
# daphne above): it carries the HTTP requests and the WebSockets
# (config/asgi.py). WSGI, HTTP only, is what Django creates by default; it
# is kept for tools that know nothing else
ASGI_APPLICATION = "config.asgi.application"
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
# Languages offered by the application; English is the fallback
LANGUAGES = [
    ("en", "English"),
    ("fr", "Français"),
]
LANGUAGE_CODE = "en"

# Where our own translations live: backend/locale/<language>/LC_MESSAGES/,
# one folder for the whole project (decision of 23.10.2026). Django looks
# here first, then in each application, then in its own translations
LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "UTC"

# Enables Django's translation system
USE_I18N = True

# Stores dates and times in UTC, with time zone information
USE_TZ = True

# ── Countries ─────────────────────────────────────────────────────────
# The list of django-countries, served by /api/countries/ and offered by
# the drop-downs of the profile: Switzerland and France first (the public
# of the site), then every country in the alphabetical order of the
# language of the request; the two also keep their alphabetical place
COUNTRIES_FIRST = ["CH", "FR"]
COUNTRIES_FIRST_REPEAT = True

# ── Static files ──────────────────────────────────────────────────────

# https://docs.djangoproject.com/en/6.1/howto/static-files/
# URL prefix of static files (CSS, JavaScript, images)
STATIC_URL = "static/"

# Folder where the collectstatic command gathers every static file, so that
# they can be served outside development
STATIC_ROOT = BASE_DIR / "staticfiles"

# ── User files ────────────────────────────────────────────────────────

# https://docs.djangoproject.com/en/6.1/topics/files/
# Folder where the files sent by the users are stored (photos, CVs, logos,
# documents): a folder of the backend, never versioned, in development; a
# Docker volume in production. Nothing serves this folder as such: every
# file goes through a view of the profiles application, which checks who
# may read it.
MEDIA_ROOT = BASE_DIR / "media"

# Prefix of the URLs Django builds for these files (the .url of a field).
# It is the address of that view, so that the links of the admin site and
# of the API open the file after the check, never directly.
MEDIA_URL = "/api/files/"

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
    # A demo account, open to anyone, writes 60 times an hour at most, any
    # other account 300 times; reading is not limited (demo/throttles.py)
    "DEFAULT_THROTTLE_CLASSES": [
        "demo.throttles.DemoWriteThrottle",
        "demo.throttles.AccountWriteThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "demo": "60/hour",
        "account": "300/hour",
    },
}

# ── Email ─────────────────────────────────────────────────────────────

# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration
# The console backend prints emails in the terminal instead of sending them.
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}
