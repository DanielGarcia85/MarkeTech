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
server. Then the public demonstration: any visitor opens a demo account by
its role, without password; a demo account cannot change its address nor
its password, and writes 60 times an hour at most.
"""

import json
import os
import shutil
import tempfile
from io import StringIO

from allauth.account.models import EmailAddress
from django.core.cache import cache
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
        self.assertEqual(User.objects.filter(email__endswith="@example.com").count(), 6)
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
        client.force_login(User.objects.get(email="candidat1@example.com"))
        mine = [spec for spec in APPLICATIONS if spec["candidate"] == "candidat1@example.com"]
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
        # Léa Martin and Quorvane, the pair the site is shown with: open
        # and closed conversations, unread on both sides
        candidate, employer = Client(), Client()
        candidate.force_login(User.objects.get(email="candidat1@example.com"))
        employer.force_login(User.objects.get(email="employeur1@example.com"))
        unread = {"count": 2, "open": 2, "closed": 0}
        self.assertEqual(candidate.get("/api/messages/unread/").json(), unread)
        self.assertEqual(employer.get("/api/messages/unread/").json(), unread)
        self.assertEqual(len(candidate.get("/api/messages/?state=open").json()), 2)
        self.assertEqual(len(candidate.get("/api/messages/?state=closed").json()), 2)
        self.assertEqual(len(employer.get("/api/messages/").json()), 6)

    @override_settings(DEBUG=True)
    def test_seed_demo_leaves_some_news_unseen(self):
        call_command("seed_demo", stdout=StringIO())
        # Two applications just received for Quorvane, one move for Léa
        unseen = [spec for spec in APPLICATIONS if spec.get("unseen")]
        self.assertEqual(StatusChange.objects.filter(seen_at=None).count(), len(unseen))
        candidate, employer = Client(), Client()
        candidate.force_login(User.objects.get(email="candidat1@example.com"))
        employer.force_login(User.objects.get(email="employeur1@example.com"))
        self.assertEqual(employer.get("/api/applications/unseen/").json(), {"count": 2})
        self.assertEqual(candidate.get("/api/applications/unseen/").json(), {"count": 1})

    @override_settings(DEBUG=True)
    def test_seed_demo_runs_once_unless_reset(self):
        call_command("seed_demo", stdout=StringIO())
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        cv = CandidateProfile.objects.get(user__email="candidat1@example.com").cv.name
        call_command("seed_demo", "--reset", stdout=StringIO())
        self.assertEqual(User.objects.filter(email__endswith="@example.com").count(), 6)
        self.assertEqual(JobOffer.objects.count(), 30)
        self.assertEqual(JobApplication.objects.count(), len(APPLICATIONS))
        # The files of the first run left the disk with their rows
        self.assertFalse(os.path.exists(os.path.join(MEDIA, cv)))

    def test_seed_demo_on_a_server_opens_no_account_by_password(self):
        # DEBUG off, as on a server: --force, and no usable password
        out = StringIO()
        call_command("seed_demo", "--force", stdout=out)
        self.assertNotIn("Demo-1234", out.getvalue())
        # Nor any address: the output goes to the journal of the server
        self.assertNotIn("@", out.getvalue())
        self.assertFalse(any(user.has_usable_password() for user in User.objects.all()))
        # The two demo accounts, the ones with the data
        demo = sorted(User.objects.filter(is_demo=True).values_list("email", flat=True))
        self.assertEqual(demo, ["candidat1@example.com", "employeur1@example.com"])

    def test_seed_demo_refuses_without_debug(self):
        # The tests run with DEBUG off, as a server does
        with self.assertRaises(CommandError):
            call_command("seed_demo", stdout=StringIO())
        self.assertEqual(User.objects.count(), 0)


class DemoAccountTests(TestCase):
    """The demo accounts: opened by a button, closed to some changes,
    limited in their writes."""

    def setUp(self):
        cache.clear()
        self.candidate = User.objects.create_user(
            email="candidat1@example.com", password=None, role="candidate", is_demo=True
        )
        self.employer = User.objects.create_user(
            email="employeur1@example.com", password=None, role="employer", is_demo=True
        )
        self.real = User.objects.create_user(
            email="real@example.org", password="Correct-horse-9", role="candidate"
        )

    def client_with_token(self, user=None):
        """A client, logged in or not, sending back its CSRF token."""
        client = Client(enforce_csrf_checks=True)
        if user:
            client.force_login(user)
        client.get("/_allauth/browser/v1/auth/session")
        client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
        return client

    def post(self, client, url, data):
        return client.post(url, data=json.dumps(data), content_type="application/json")

    def test_a_visitor_opens_a_demo_account_by_its_role(self):
        client = self.client_with_token()
        # Not without the terms accepted
        response = self.post(client, "/api/demo/login/", {"role": "employer"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(list(response.json()), ["terms"])
        response = self.post(client, "/api/demo/login/", {"role": "employer", "terms": True})
        self.assertEqual(response.json(), {"email": "employeur1@example.com", "role": "employer"})
        session = client.get("/_allauth/browser/v1/auth/session").json()
        self.assertEqual(session["data"]["user"]["email"], "employeur1@example.com")
        # No password opens it: it has none that works
        self.assertFalse(self.employer.has_usable_password())
        # A login gives a new CSRF token, as for any login: the page reads
        # it again from the cookie at each request (api/http.ts)
        client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
        # Another role, or no demo account of that role: not found
        admin = {"role": "admin", "terms": True}
        self.assertEqual(self.post(client, "/api/demo/login/", admin).status_code, 404)
        User.objects.filter(pk=self.candidate.pk).update(is_demo=False)
        candidate = {"role": "candidate", "terms": True}
        self.assertEqual(self.post(client, "/api/demo/login/", candidate).status_code, 404)

    def test_a_demo_account_keeps_its_address_and_password(self):
        client = self.client_with_token(self.candidate)
        for url, data in (
            ("/_allauth/browser/v1/account/email", {"email": "mine@example.org"}),
            ("/_allauth/browser/v1/account/password/change", {"new_password": "Another-horse-9"}),
        ):
            response = self.post(client, url, data)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json()["errors"][0]["code"], "demo_account")
        # Reading the addresses stays allowed
        self.assertEqual(client.get("/_allauth/browser/v1/account/email").status_code, 200)
        # Another account is not stopped here
        other = self.client_with_token(self.real)
        response = self.post(
            other, "/_allauth/browser/v1/account/email", {"email": "new@example.org"}
        )
        self.assertNotEqual(response.status_code, 403)

    def test_a_demo_account_writes_sixty_times_an_hour(self):
        client, other = self.client_with_token(self.candidate), self.client_with_token(self.real)
        CandidateProfile.objects.create(user=self.candidate)
        CandidateProfile.objects.create(user=self.real)
        # Writes that fail count as much as the others: no offer 9999
        for _ in range(60):
            self.assertEqual(self.post(client, "/api/favorites/", {"offer": 9999}).status_code, 400)
        self.assertEqual(self.post(client, "/api/favorites/", {"offer": 9999}).status_code, 429)
        # Reading goes on, and another account is not limited
        self.assertEqual(client.get("/api/favorites/").status_code, 200)
        for _ in range(61):
            self.assertEqual(self.post(other, "/api/favorites/", {"offer": 9999}).status_code, 400)
