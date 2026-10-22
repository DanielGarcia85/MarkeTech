# backend/demo/tests.py

"""
Demo tests — the seed_demo command
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the seed_demo command, which fills a development database with test
accounts, offers, applications, favorites and messages: everything it
announces is there, the files it writes are real PDFs and the logos real PNGs, it runs
once only unless --reset, and it refuses to run with DEBUG off, as on a
server.
"""

import os
import shutil
import tempfile
from io import StringIO

from allauth.account.models import EmailAddress
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from accounts.models import User
from applications.models import Attachment, JobApplication, StatusChange
from demo.management.commands.seed_demo import APPLICATIONS, FAVORITES
from favorites.models import Favorite
from messaging.models import Message
from offers.models import JobOffer
from profiles.models import CandidateDocument, CandidateProfile, EmployerProfile

# Files land here during the tests, never in the media folder of the project
MEDIA = tempfile.mkdtemp(prefix="marketech-tests-")


@override_settings(MEDIA_ROOT=MEDIA)
class SeedDemoTests(TestCase):
    """The seed_demo command: six accounts able to log in, their profiles
    with their files and logos, thirty offers, most of them in the public
    list, the applications with their history, eight favorites, the
    conversations; once only, unless --reset; never with DEBUG off."""

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
        # Every company has a logo, a real PNG, that the public list links to
        self.assertEqual(EmployerProfile.objects.exclude(logo="").count(), 3)
        for profile in EmployerProfile.objects.all():
            with open(os.path.join(MEDIA, profile.logo.name), "rb") as logo:
                self.assertTrue(logo.read().startswith(b"\x89PNG"))
        offers = Client().get("/api/offers/").json()["results"]
        self.assertTrue(all(o["company"]["logo"] for o in offers))
        # The applications, their files copied, their states dated
        self.assertEqual(JobApplication.objects.count(), len(APPLICATIONS))
        letters = sum(spec["letter"] for spec in APPLICATIONS)
        self.assertEqual(JobApplication.objects.exclude(cover_letter="").count(), letters)
        documents = sum(len(spec["documents"]) for spec in APPLICATIONS)
        self.assertEqual(Attachment.objects.count(), documents)
        self.assertEqual(
            sorted(set(JobApplication.objects.values_list("status", flat=True))),
            ["accepted", "in_progress", "received", "rejected"],
        )
        # One line of history at the creation, one per move since
        moves = sum(len(spec["moves"]) for spec in APPLICATIONS)
        self.assertEqual(StatusChange.objects.count(), len(APPLICATIONS) + moves)
        accepted = JobApplication.objects.filter(status="accepted").order_by("created_at").first()
        self.assertLess(accepted.created_at, accepted.history.last().changed_at)
        for application in JobApplication.objects.all():
            self.assertLessEqual(application.offer.published_at, application.created_at)
        # The API serves them to their candidate
        client = Client()
        client.force_login(User.objects.get(email="candidat1@test.com"))
        mine = [spec for spec in APPLICATIONS if spec["candidate"] == "candidat1@test.com"]
        self.assertEqual(len(client.get("/api/applications/").json()), len(mine))
        # The favorites, dated, one on an offer closed since
        self.assertEqual(Favorite.objects.count(), len(FAVORITES))
        self.assertEqual(Favorite.objects.filter(offer__status="closed").count(), 1)
        self.assertEqual(Favorite.objects.filter(created_at__date=timezone.now().date()).count(), 0)
        self.assertEqual(len(client.get("/api/favorites/").json()), 4)
        self.assertEqual(sum(o["favorite"] for o in client.get("/api/offers/").json()["results"]), 3)

    @override_settings(DEBUG=True)
    def test_seed_demo_writes_the_conversations(self):
        call_command("seed_demo", stdout=StringIO())
        written = sum(len(spec.get("messages", [])) for spec in APPLICATIONS)
        self.assertEqual(Message.objects.count(), written)
        # Only on applications taken up: never on one still received
        self.assertFalse(Message.objects.filter(application__status="received").exists())
        # Dated in the past, each conversation in its order, read after sent
        for message in Message.objects.exclude(read_at=None):
            self.assertLess(message.sent_at, message.read_at)
        self.assertFalse(Message.objects.filter(sent_at__gt=timezone.now()).exists())
        # Léa Martin and Lémantech, the pair the site is shown with: open
        # and closed conversations, unread on both sides
        candidate, employer = Client(), Client()
        candidate.force_login(User.objects.get(email="candidat1@test.com"))
        employer.force_login(User.objects.get(email="employeur1@test.com"))
        unread = {"count": 2, "open": 2, "closed": 0}
        self.assertEqual(candidate.get("/api/messages/unread/").json(), unread)
        self.assertEqual(employer.get("/api/messages/unread/").json(), unread)
        self.assertEqual(len(candidate.get("/api/messages/?state=open").json()), 2)
        self.assertEqual(len(candidate.get("/api/messages/?state=closed").json()), 2)
        self.assertEqual(len(employer.get("/api/messages/").json()), 6)

    @override_settings(DEBUG=True)
    def test_seed_demo_leaves_some_news_unseen(self):
        call_command("seed_demo", stdout=StringIO())
        # Two applications just received for Lémantech, one move for Léa
        unseen = [spec for spec in APPLICATIONS if spec.get("unseen")]
        self.assertEqual(StatusChange.objects.filter(seen_at=None).count(), len(unseen))
        candidate, employer = Client(), Client()
        candidate.force_login(User.objects.get(email="candidat1@test.com"))
        employer.force_login(User.objects.get(email="employeur1@test.com"))
        self.assertEqual(employer.get("/api/applications/unseen/").json(), {"count": 2})
        self.assertEqual(candidate.get("/api/applications/unseen/").json(), {"count": 1})

    @override_settings(DEBUG=True)
    def test_seed_demo_runs_once_unless_reset(self):
        call_command("seed_demo", stdout=StringIO())
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        cv = CandidateProfile.objects.get(user__email="candidat1@test.com").cv.name
        call_command("seed_demo", "--reset", stdout=StringIO())
        self.assertEqual(User.objects.filter(email__endswith="@test.com").count(), 6)
        self.assertEqual(JobOffer.objects.count(), 30)
        self.assertEqual(JobApplication.objects.count(), len(APPLICATIONS))
        # The files of the first run left the disk with their rows
        self.assertFalse(os.path.exists(os.path.join(MEDIA, cv)))

    def test_seed_demo_refuses_without_debug(self):
        # The tests run with DEBUG off, as a server does
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertEqual(User.objects.count(), 0)
