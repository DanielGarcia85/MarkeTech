# backend/accounts/tests.py

"""
Account tests — the sign-up, login and password reset journeys
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the authentication API as the frontend will use it: JSON requests to
the browser client of allauth, CSRF protection enforced, e-mails read from
the test outbox, in the language of the request. Does not test allauth
itself, only our configuration of it.
"""

import json
import re
from urllib.parse import unquote

from django.core import mail
from django.core.cache import cache
from django.test import Client, TestCase

from .adapter import display_name
from .models import User

API = "/_allauth/browser/v1/"
EMAIL = "Lea.Doe@Example.com"
PASSWORD = "Correct-horse-9"
NAMES = {"first_name": "Léa", "last_name": "Doe"}


class AuthenticationApiTests(TestCase):
    """Journeys of a visitor who signs up, logs in and resets a password."""

    def setUp(self):
        # Like a real browser, the client must send back the CSRF token
        self.client = Client(enforce_csrf_checks=True)
        # The rate limits of allauth live in the cache, which survives from
        # one test to the next: without this, the second sign-up of the same
        # address would get no e-mail
        cache.clear()

    def api(self, method, path, data=None):
        """Call the API as the frontend does, with the CSRF token if any."""
        headers = {}
        token = self.client.cookies.get("csrftoken")
        if token:
            headers["HTTP_X_CSRFTOKEN"] = token.value
        if method == "GET":
            return self.client.get(API + path, **headers)
        if method == "DELETE":
            return self.client.delete(API + path, **headers)
        return self.client.post(
            API + path,
            data=json.dumps(data),
            content_type="application/json",
            **headers,
        )

    def key_from_mail(self, path):
        """Return the one-time key of the last e-mail, read from its link."""
        body = mail.outbox[-1].body
        match = re.search(rf"{path}(\S+)", body)
        self.assertIsNotNone(match, "no link to the frontend in the e-mail")
        return unquote(match.group(1))

    def sign_up(self):
        """Sign up with a mixed-case address, the names and the candidate role."""
        # The first call sets the CSRF cookie that the following ones need
        self.api("GET", "auth/session")
        return self.api(
            "POST",
            "auth/signup",
            {"email": EMAIL, "password": PASSWORD, "role": "candidate", **NAMES},
        )

    def test_signup_requires_the_names_and_a_role(self):
        self.api("GET", "auth/session")
        response = self.api(
            "POST", "auth/signup", {"email": EMAIL, "password": PASSWORD}
        )
        self.assertEqual(response.status_code, 400)
        missing = {error["param"] for error in response.json()["errors"]}
        self.assertEqual(missing, {"first_name", "last_name", "role"})
        self.assertFalse(User.objects.exists())

    def test_signup_stores_the_address_in_lower_case_with_names_and_role(self):
        response = self.sign_up()
        # 401: the account exists, but its address is not verified yet
        self.assertEqual(response.status_code, 401)
        user = User.objects.get()
        self.assertEqual(user.email, "lea.doe@example.com")
        self.assertEqual(user.first_name, "Léa")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.role, User.Role.CANDIDATE)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/account/verify-email/", mail.outbox[0].body)

    def test_login_is_refused_until_the_address_is_verified(self):
        self.sign_up()
        response = self.api(
            "POST", "auth/login", {"email": EMAIL, "password": PASSWORD}
        )
        self.assertEqual(response.status_code, 401)
        pending = [
            flow["id"]
            for flow in response.json()["data"]["flows"]
            if flow.get("is_pending")
        ]
        self.assertEqual(pending, ["verify_email"])

    def test_verified_user_logs_in_whatever_the_case_of_the_address(self):
        self.sign_up()
        key = self.key_from_mail("/account/verify-email/")
        response = self.api("POST", "auth/email/verify", {"key": key})
        self.assertEqual(response.status_code, 401)

        response = self.api(
            "POST",
            "auth/login",
            {"email": "LEA.DOE@EXAMPLE.COM", "password": PASSWORD},
        )
        self.assertEqual(response.status_code, 200)
        user = response.json()["data"]["user"]
        self.assertEqual(user["email"], "lea.doe@example.com")
        self.assertEqual(user["display"], "Léa Doe")
        self.assertEqual(user["role"], "candidate")

        self.assertEqual(self.api("GET", "auth/session").status_code, 200)
        self.assertEqual(self.api("DELETE", "auth/session").status_code, 401)
        self.assertEqual(self.api("GET", "auth/session").status_code, 401)

    def test_password_reset_by_the_link_of_the_email(self):
        self.sign_up()
        key = self.key_from_mail("/account/verify-email/")
        self.api("POST", "auth/email/verify", {"key": key})

        response = self.api(
            "POST", "auth/password/request", {"email": "lea.doe@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        key = self.key_from_mail("/account/password/reset/")
        response = self.api(
            "POST",
            "auth/password/reset",
            {"key": key, "password": "New-horse-10"},
        )
        self.assertEqual(response.status_code, 401)

        response = self.api(
            "POST",
            "auth/login",
            {"email": "lea.doe@example.com", "password": "New-horse-10"},
        )
        self.assertEqual(response.status_code, 200)

    def test_emails_follow_the_language_of_the_request(self):
        # fr-CH is not offered: Django falls back to plain fr
        self.client = Client(
            enforce_csrf_checks=True,
            headers={"Accept-Language": "fr-CH,fr;q=0.9,en;q=0.8"},
        )
        self.sign_up()
        self.assertEqual(
            mail.outbox[0].subject,
            "[MarkeTech] Confirmez votre adresse e-mail",
        )
        self.assertIn("Bonjour Léa,", mail.outbox[0].body)

    def test_emails_fall_back_to_english(self):
        self.client = Client(
            enforce_csrf_checks=True, headers={"Accept-Language": "de"}
        )
        self.sign_up()
        self.assertEqual(
            mail.outbox[0].subject, "[MarkeTech] Confirm your e-mail address"
        )
        self.assertIn("Hello Léa,", mail.outbox[0].body)


class DisplayNameTests(TestCase):
    """The name shown for a user, with and without the names."""

    def test_full_name_when_the_names_are_known(self):
        user = User(email="lea.doe@example.com", **NAMES)
        self.assertEqual(display_name(user), "Léa Doe")

    def test_address_when_the_names_are_unknown(self):
        # An account created before the names were asked at sign-up
        user = User(email="lea.doe@example.com")
        self.assertEqual(display_name(user), "lea.doe@example.com")
