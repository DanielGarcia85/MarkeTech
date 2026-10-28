# backend/accounts/tests.py

"""
Account tests — the sign-up, login and password reset journeys
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the authentication API as the frontend will use it: JSON requests to
the browser client of allauth, CSRF protection enforced, e-mails read from
the test outbox, in the language of the request; then the changes a
logged-in user makes to their account (address, password) and the security
notices they bring; then the language a login leaves on the account, for
its notifications. Does not test allauth itself, only our configuration of
it.
"""

import json
import re
import smtplib
from unittest import mock
from urllib.parse import unquote

from allauth.account.models import EmailAddress
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
            {"email": EMAIL, "password": PASSWORD, "role": "candidate", "terms": True, **NAMES},
        )

    def test_signup_requires_the_names_a_role_and_the_terms(self):
        self.api("GET", "auth/session")
        response = self.api(
            "POST", "auth/signup", {"email": EMAIL, "password": PASSWORD}
        )
        self.assertEqual(response.status_code, 400)
        missing = {error["param"] for error in response.json()["errors"]}
        self.assertEqual(missing, {"first_name", "last_name", "role", "terms"})
        # The box left unticked is refused like a missing field
        response = self.api(
            "POST",
            "auth/signup",
            {"email": EMAIL, "password": PASSWORD, "role": "candidate", "terms": False, **NAMES},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual([error["param"] for error in response.json()["errors"]], ["terms"])
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
        # The acceptance of the terms is dated
        self.assertIsNotNone(user.terms_accepted_at)
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
        # The security notice of the reset, sent once it is done
        notice = [m for m in mail.outbox if m.subject == "The password of your account was reset"]
        self.assertEqual(len(notice), 1)
        self.assertEqual(notice[0].to, ["lea.doe@example.com"])

    def test_emails_follow_the_language_of_the_request(self):
        # fr-CH is not offered: Django falls back to plain fr
        self.client = Client(
            enforce_csrf_checks=True,
            headers={"Accept-Language": "fr-CH,fr;q=0.9,en;q=0.8"},
        )
        self.sign_up()
        self.assertEqual(
            mail.outbox[0].subject,
            "Confirmez votre adresse e-mail",
        )
        self.assertIn("Bonjour Léa,", mail.outbox[0].body)

    def test_emails_fall_back_to_english(self):
        self.client = Client(
            enforce_csrf_checks=True, headers={"Accept-Language": "de"}
        )
        self.sign_up()
        self.assertEqual(
            mail.outbox[0].subject, "Confirm your e-mail address"
        )
        self.assertIn("Hello Léa,", mail.outbox[0].body)


class AccountChangesTests(TestCase):
    """A logged-in user changes the address or the password of the account."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            email="lea.doe@example.com", password=PASSWORD, role="candidate", **NAMES
        )
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True, primary=True
        )
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.user)
        # The session route sets the CSRF cookie; every call then sends it
        self.client.get(API + "auth/session")
        self.client.defaults["HTTP_X_CSRFTOKEN"] = self.client.cookies["csrftoken"].value

    def post(self, path, data):
        return self.client.post(
            API + path, data=json.dumps(data), content_type="application/json"
        )

    def test_the_address_changes_once_the_new_one_is_confirmed(self):
        response = self.post("account/email", {"email": "New.Address@Example.com"})
        self.assertEqual(response.status_code, 200)
        # The e-mail goes to the new address, with the words of a change, not
        # those of a sign-up; the current address is untouched meanwhile
        self.assertEqual(mail.outbox[-1].to, ["new.address@example.com"])
        self.assertEqual(mail.outbox[-1].subject, "Confirm your new e-mail address")
        self.assertIn("stays in force", mail.outbox[-1].body)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "lea.doe@example.com")

        key = unquote(re.search(r"verify-email/(\S+)", mail.outbox[-1].body).group(1))
        response = self.post("auth/email/verify", {"key": key})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new.address@example.com")
        # One address only: the old one is gone
        self.assertEqual(
            list(EmailAddress.objects.filter(user=self.user).values_list("email", flat=True)),
            ["new.address@example.com"],
        )
        # The old address is told, with where the change came from
        notice = mail.outbox[-1]
        self.assertEqual(notice.to, ["lea.doe@example.com"])
        self.assertEqual(notice.subject, "The e-mail address of your account has changed")
        self.assertIn("from lea.doe@example.com to new.address@example.com", notice.body)
        self.assertIn("- IP address: 127.0.0.1", notice.body)
        self.assertIn("(Geneva time)", notice.body)

    def test_a_cancelled_change_tells_the_current_address(self):
        self.post("account/email", {"email": "new.address@example.com"})
        response = self.client.delete(
            API + "account/email",
            data=json.dumps({"email": "new.address@example.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        notice = mail.outbox[-1]
        self.assertEqual(notice.to, ["lea.doe@example.com"])
        self.assertEqual(notice.subject, "An e-mail address was removed from your account")
        self.assertIn("new.address@example.com was removed", notice.body)

    def test_the_password_changes_with_the_current_one(self):
        response = self.post(
            "account/password/change",
            {"current_password": "wrong", "new_password": "New-horse-10"},
        )
        self.assertEqual(response.status_code, 400)
        response = self.post(
            "account/password/change",
            {"current_password": PASSWORD, "new_password": "New-horse-10"},
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("New-horse-10"))
        # Still logged in afterwards
        self.assertEqual(self.client.get(API + "auth/session").status_code, 200)
        # The security notice, in the language of the request
        self.assertEqual(mail.outbox[-1].subject, "The password of your account has changed")

    def test_a_notice_that_fails_to_leave_never_breaks_the_change(self):
        # The mail server refuses the login, as it did on 28.10.2026
        refused = smtplib.SMTPAuthenticationError(535, b"5.7.0 Invalid login or password")
        with (
            mock.patch("django.core.mail.message.EmailMessage.send", side_effect=refused),
            self.assertLogs("accounts.adapter", level="WARNING") as logs,
        ):
            response = self.post(
                "account/password/change",
                {"current_password": PASSWORD, "new_password": "New-horse-10"},
            )
        # The change is answered as done, and is done; the session stays
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("New-horse-10"))
        self.assertEqual(self.client.get(API + "auth/session").status_code, 200)
        # The failure is in the journal, with the account and no address
        expected = f"Security notice password_changed to user {self.user.pk} not sent"
        self.assertIn(expected, logs.output[0])
        self.assertIn("SMTPAuthenticationError", logs.output[0])
        self.assertNotIn("example.com", "".join(logs.output))

    def test_the_security_notices_speak_french(self):
        self.client.defaults["HTTP_ACCEPT_LANGUAGE"] = "fr"
        self.post(
            "account/password/change",
            {"current_password": PASSWORD, "new_password": "New-horse-10"},
        )
        notice = mail.outbox[-1]
        self.assertEqual(notice.subject, "Le mot de passe de votre compte a changé")
        # Made logged in: the greeting knows the user
        self.assertIn("Bonjour Léa,", notice.body)
        self.assertIn("écrivez-nous à contact@marketech.ch", notice.body)
        self.assertIn("(heure de Genève)", notice.body)


class DisplayNameTests(TestCase):
    """The name shown for a user, with and without the names."""

    def test_full_name_when_the_names_are_known(self):
        user = User(email="lea.doe@example.com", **NAMES)
        self.assertEqual(display_name(user), "Léa Doe")

    def test_address_when_the_names_are_unknown(self):
        # An account created before the names were asked at sign-up
        user = User(email="lea.doe@example.com")
        self.assertEqual(display_name(user), "lea.doe@example.com")


class LanguageTests(TestCase):
    """The language of a user, kept at every login for the notifications."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            email="lea.doe@example.com", password=PASSWORD, role="candidate", **NAMES
        )
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True, primary=True
        )

    def log_in(self, language):
        """Log in through the API, the interface in this language."""
        client = Client(enforce_csrf_checks=True, headers={"Accept-Language": language})
        client.get(API + "auth/session")
        token = client.cookies["csrftoken"].value
        return client.post(
            API + "auth/login",
            data=json.dumps({"email": self.user.email, "password": PASSWORD}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )

    def test_a_new_account_has_no_language_and_gets_the_notifications(self):
        self.assertEqual(self.user.language, "")
        self.assertTrue(self.user.notify_by_email)

    def test_every_login_keeps_the_language_of_the_interface(self):
        self.assertEqual(self.log_in("fr").status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.language, "fr")
        self.log_in("en")
        self.user.refresh_from_db()
        self.assertEqual(self.user.language, "en")
        # A language the site does not offer: Django falls back to English
        self.log_in("de")
        self.user.refresh_from_db()
        self.assertEqual(self.user.language, "en")

    def test_the_login_of_a_demo_account_keeps_it_too(self):
        self.user.is_demo = True
        self.user.save()
        client = Client(enforce_csrf_checks=True, headers={"Accept-Language": "fr"})
        client.get(API + "auth/session")
        response = client.post(
            "/api/demo/login/",
            data=json.dumps({"role": "candidate", "terms": True}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.language, "fr")
