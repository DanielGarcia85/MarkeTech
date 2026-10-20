# backend/demo/tests.py

"""
Demo tests — the seed_demo command
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the seed_demo command, which fills a development database with test
accounts, offers and applications: everything it announces is there, the
files it writes are real PDFs, it runs once only unless --reset, and it
refuses to run with DEBUG off, as on a server.
"""

import os
import shutil
import tempfile
from io import StringIO

from allauth.account.models import EmailAddress
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase, override_settings

from accounts.models import User
from applications.models import Attachment, JobApplication, StatusChange
from demo.management.commands.seed_demo import APPLICATIONS
from offers.models import JobOffer
from profiles.models import CandidateDocument, CandidateProfile, EmployerProfile

# Files land here during the tests, never in the media folder of the project
MEDIA = tempfile.mkdtemp(prefix="marketech-tests-")


@override_settings(MEDIA_ROOT=MEDIA)
class SeedDemoTests(TestCase):
    """The seed_demo command: six accounts able to log in, their profiles
    with their files, thirty offers, most of them in the public list, nine
    applications with their history; once only, unless --reset; never with
    DEBUG off."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        # The files of the previous test: the rows are rolled back between
        # the tests, the files are not
        shutil.rmtree(MEDIA, ignore_errors=True)

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
    def test_seed_demo_writes_the_files_and_the_applications(self):
        call_command("seed_demo", stdout=StringIO())
        # Every candidate has a CV and at least one document, real PDFs
        self.assertEqual(CandidateProfile.objects.exclude(cv="").count(), 3)
        self.assertEqual(CandidateDocument.objects.count(), 4)
        for profile in CandidateProfile.objects.all():
            with open(os.path.join(MEDIA, profile.cv.name), "rb") as cv:
                self.assertTrue(cv.read().startswith(b"%PDF-1.4"))
        # The applications, their files copied, their states dated
        self.assertEqual(JobApplication.objects.count(), 9)
        self.assertEqual(JobApplication.objects.exclude(cover_letter="").count(), 6)
        self.assertEqual(Attachment.objects.count(), 7)
        self.assertEqual(
            sorted(set(JobApplication.objects.values_list("status", flat=True))),
            ["accepted", "in_progress", "received", "rejected"],
        )
        # One line of history at the creation, one per move since
        moves = sum(len(spec["moves"]) for spec in APPLICATIONS)
        self.assertEqual(StatusChange.objects.count(), 9 + moves)
        accepted = JobApplication.objects.filter(status="accepted").order_by("created_at").first()
        self.assertLess(accepted.created_at, accepted.history.last().changed_at)
        for application in JobApplication.objects.all():
            self.assertLessEqual(application.offer.published_at, application.created_at)
        # The API serves them to their candidate
        client = Client()
        client.force_login(User.objects.get(email="candidat1@test.com"))
        self.assertEqual(len(client.get("/api/applications/").json()), 3)

    @override_settings(DEBUG=True)
    def test_seed_demo_runs_once_unless_reset(self):
        call_command("seed_demo", stdout=StringIO())
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        cv = CandidateProfile.objects.get(user__email="candidat1@test.com").cv.name
        call_command("seed_demo", "--reset", stdout=StringIO())
        self.assertEqual(User.objects.filter(email__endswith="@test.com").count(), 6)
        self.assertEqual(JobOffer.objects.count(), 30)
        self.assertEqual(JobApplication.objects.count(), 9)
        # The files of the first run left the disk with their rows
        self.assertFalse(os.path.exists(os.path.join(MEDIA, cv)))

    def test_seed_demo_refuses_without_debug(self):
        # The tests run with DEBUG off, as a server does
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertEqual(User.objects.count(), 0)
