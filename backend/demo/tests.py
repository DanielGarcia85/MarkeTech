# backend/demo/tests.py

"""
Demo tests — the seed_demo command
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the seed_demo command, which fills a development database with test
accounts and offers: everything it announces is there, it runs once only
unless --reset, and it refuses to run with DEBUG off, as on a server.
"""

from io import StringIO

from allauth.account.models import EmailAddress
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase, override_settings

from accounts.models import User
from offers.models import JobOffer
from profiles.models import EmployerProfile


class SeedDemoTests(TestCase):
    """The seed_demo command: six accounts able to log in, their profiles
    and thirty offers, most of them in the public list; once only, unless
    --reset; never with DEBUG off."""

    @override_settings(DEBUG=True)
    def test_seed_demo_fills_the_database(self):
        out = StringIO()
        call_command("seed_demo", stdout=out)
        self.assertEqual(User.objects.filter(email__endswith="@test.com").count(), 6)
        # Every address is verified: allauth would refuse the login otherwise
        self.assertEqual(EmailAddress.objects.filter(verified=True, primary=True).count(), 6)
        # And the terms accepted, as a sign-up would have left them
        self.assertEqual(User.objects.filter(terms_accepted_at__isnull=False).count(), 6)
        self.assertEqual(EmployerProfile.objects.exclude(company_name="").count(), 3)
        self.assertEqual(JobOffer.objects.count(), 30)
        self.assertEqual(JobOffer.objects.filter(status="published").count(), 24)
        # A closed offer was published once: it has a date too
        self.assertEqual(JobOffer.objects.filter(published_at__isnull=True).count(), 3)
        # The offers of the French employer are in euros
        self.assertEqual(JobOffer.objects.filter(currency="EUR").count(), 10)
        self.assertEqual(Client().get("/api/offers/").json()["count"], 24)
        self.assertIn("Demo-1234", out.getvalue())

    @override_settings(DEBUG=True)
    def test_seed_demo_runs_once_unless_reset(self):
        call_command("seed_demo", stdout=StringIO())
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", "--reset", stdout=StringIO())
        self.assertEqual(User.objects.filter(email__endswith="@test.com").count(), 6)
        self.assertEqual(JobOffer.objects.count(), 30)

    def test_seed_demo_refuses_without_debug(self):
        # The tests run with DEBUG off, as a server does
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertEqual(User.objects.count(), 0)
