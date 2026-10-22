# backend/messaging/tests.py

"""
Messaging tests — the messages, their conversation and its API
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the model of the messages: a message belongs to an application,
reads in the order it was sent, is unread until the other participant
opens it, cannot be empty, and goes with its application, whether the
application is withdrawn or deleted with its offer or with an account.
Then the API as the pages will use it: the conversation opens when the
employer moves the application in progress, with an optional first
message, both participants write while it is in progress, reading marks
the other's messages read, a decision closes it with an optional last
message and a move back in progress opens it again; nobody else reaches
it; the list of the conversations and the unread counts.
"""

import json
import shutil
import tempfile

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings

from accounts.models import User
from applications.models import JobApplication
from offers.models import JobOffer
from profiles.models import CandidateProfile, EmployerProfile

from .models import Message

PASSWORD = "Correct-horse-9"

# Files land here during the tests, never in the media folder of the project
MEDIA = tempfile.mkdtemp(prefix="marketech-tests-")

# What a valid new offer needs
OFFER = {
    "title": "Python developer",
    "description": "Django and Vue.",
    "city": "Geneva",
    "country": "CH",
    "contract": "permanent",
}


@override_settings(MEDIA_ROOT=MEDIA)
class MessageModelTests(TestCase):
    """The messages of the conversation of an application."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        # The files of the previous test: the rows are rolled back between
        # the tests, the files are not
        shutil.rmtree(MEDIA, ignore_errors=True)
        self.candidate = User.objects.create_user(
            email="cand@example.com", password=PASSWORD, role="candidate"
        )
        self.employer = User.objects.create_user(
            email="emp@example.com", password=PASSWORD, role="employer"
        )
        profile = CandidateProfile.objects.create(user=self.candidate)
        company = EmployerProfile.objects.create(user=self.employer, company_name="Acme")
        self.offer = JobOffer.objects.create(employer=company, status="published", **OFFER)
        self.application = JobApplication.objects.create(
            offer=self.offer,
            candidate=profile,
            cv=SimpleUploadedFile("cv.pdf", b"%PDF-1.4 fake"),
            status="in_progress",
        )

    def write(self, author, body):
        return Message.objects.create(application=self.application, author=author, body=body)

    def test_a_conversation_reads_in_the_order_it_was_written(self):
        first = self.write(self.employer, "Hello, your profile interests us.")
        second = self.write(self.candidate, "Thank you, I am available.")
        third = self.write(self.employer, "Shall we meet on Monday?")
        self.assertEqual(list(self.application.messages.all()), [first, second, third])
        # Unread until the other participant opens the conversation
        self.assertEqual(self.application.messages.filter(read_at__isnull=True).count(), 3)

    def test_a_message_cannot_be_empty(self):
        # The database refuses it; atomic() keeps the test transaction usable
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.write(self.employer, "")
        self.assertEqual(Message.objects.count(), 0)

    def test_the_messages_go_with_their_application(self):
        self.write(self.employer, "Hello.")
        self.write(self.candidate, "Hello to you.")
        self.application.delete()
        self.assertEqual(Message.objects.count(), 0)

    def test_the_messages_go_with_the_offer_or_an_account(self):
        self.write(self.employer, "Hello.")
        self.offer.delete()
        self.assertEqual(Message.objects.count(), 0)
        # An account deleted: its profile, its applications, their messages
        offer = JobOffer.objects.create(
            employer=EmployerProfile.objects.get(user=self.employer), status="published", **OFFER
        )
        self.application = JobApplication.objects.create(
            offer=offer,
            candidate=CandidateProfile.objects.get(user=self.candidate),
            cv=SimpleUploadedFile("cv.pdf", b"%PDF-1.4 fake"),
        )
        self.write(self.employer, "Hello again.")
        self.candidate.delete()
        self.assertEqual(Message.objects.count(), 0)


@override_settings(MEDIA_ROOT=MEDIA)
class MessagingApiTests(TestCase):
    """The conversation of an application through the API."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        shutil.rmtree(MEDIA, ignore_errors=True)
        cache.clear()
        self.candidate = User.objects.create_user(
            email="cand@example.com",
            password=PASSWORD,
            role="candidate",
            first_name="Léa",
            last_name="Martin",
        )
        self.employer = User.objects.create_user(
            email="emp@example.com", password=PASSWORD, role="employer"
        )
        self.profile = CandidateProfile.objects.create(user=self.candidate)
        company = EmployerProfile.objects.create(user=self.employer, company_name="Acme")
        self.offer = JobOffer.objects.create(employer=company, status="published", **OFFER)
        self.application = self.apply(self.offer)
        self.url = "/api/applications/%d/messages/" % self.application.pk

    # ── Helpers ───────────────────────────────────────────────────────

    def apply(self, offer):
        """An application of the candidate to the offer, received."""
        cv = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 fake")
        return JobApplication.objects.create(offer=offer, candidate=self.profile, cv=cv)

    def new_offer(self, title):
        """Another published offer of the same employer."""
        fields = {**OFFER, "title": title}
        return JobOffer.objects.create(employer=self.offer.employer, status="published", **fields)

    def titles(self, client, url):
        """The titles of the offers of a list of conversations, in order."""
        return [c["offer"]["title"] for c in client.get(url).json()]

    def unread(self, client):
        return client.get("/api/messages/unread/").json()

    def login(self, user):
        """A client logged in as the user, with the CSRF token a browser
        would send back (enforced, as in the other API tests)."""
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        client.get("/_allauth/browser/v1/auth/session")
        client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
        return client

    def post(self, client, url, data):
        return client.post(url, data=json.dumps(data), content_type="application/json")

    def move(self, client, status, message="", application=None):
        """The employer moves the application, with a message or not."""
        application = application or self.application
        url = "/api/applications/%d/status/" % application.pk
        return self.post(client, url, {"status": status, "message": message})

    # ── The conversation ──────────────────────────────────────────────

    def test_the_conversation_opens_with_the_move_in_progress(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        # Received: nobody writes yet, and there is nothing to read
        for client in (candidate, employer):
            response = self.post(client, self.url, {"body": "Hello"})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.json(),
                {"non_field_errors": ["You can write only while the application is in progress."]},
            )
        data = candidate.get(self.url).json()
        self.assertEqual((data["open"], data["messages"]), (False, []))
        # The move in progress carries the first message
        response = self.move(employer, "in_progress", "  Your profile interests us.  ")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post(candidate, self.url, {"body": "Thank you!"}).status_code, 201)
        self.assertEqual(self.post(employer, self.url, {"body": "Monday 10 am?"}).status_code, 201)
        data = candidate.get(self.url).json()
        self.assertTrue(data["open"])
        self.assertEqual(data["other"], "Acme")
        self.assertEqual(data["offer"]["title"], "Python developer")
        self.assertEqual(
            [(m["body"], m["mine"]) for m in data["messages"]],
            [
                ("Your profile interests us.", False),
                ("Thank you!", True),
                ("Monday 10 am?", False),
            ],
        )
        self.assertEqual(employer.get(self.url).json()["other"], "Léa Martin")

    def test_reading_marks_the_other_s_messages_read(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        self.move(employer, "in_progress", "First")
        self.post(candidate, self.url, {"body": "Answer"})
        # The employer has not opened the conversation since: the answer is unread
        data = candidate.get(self.url).json()
        self.assertIsNotNone(data["messages"][0]["read_at"])
        self.assertIsNone(data["messages"][1]["read_at"])
        employer.get(self.url)
        self.assertEqual(Message.objects.filter(read_at__isnull=True).count(), 0)

    def test_a_decision_closes_the_conversation_and_a_move_back_opens_it(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        self.move(employer, "in_progress")
        # A move without a message writes nothing
        self.assertEqual(Message.objects.count(), 0)
        self.post(candidate, self.url, {"body": "Any news?"})
        self.move(employer, "rejected", "We chose another profile, thank you.")
        data = candidate.get(self.url).json()
        self.assertFalse(data["open"])
        self.assertEqual(data["messages"][-1]["body"], "We chose another profile, thank you.")
        for client in (candidate, employer):
            self.assertEqual(self.post(client, self.url, {"body": "One more"}).status_code, 400)
        # Moved back in progress: the conversation goes on where it was
        self.move(employer, "in_progress")
        response = self.post(candidate, self.url, {"body": "Glad to hear!"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.application.messages.count(), 3)

    def test_a_decision_straight_from_received_writes_one_closed_conversation(self):
        employer = self.login(self.employer)
        self.move(employer, "accepted", "Welcome aboard: call me on 022 000 00 10.")
        data = self.login(self.candidate).get(self.url).json()
        self.assertEqual((data["open"], len(data["messages"])), (False, 1))

    def test_what_is_written_is_checked(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        self.move(employer, "in_progress")
        response = self.post(candidate, self.url, {"body": "   "})
        self.assertEqual(response.json(), {"body": ["Write a message."]})
        response = self.post(candidate, self.url, {"body": "x" * 2001})
        self.assertEqual(response.json(), {"body": ["A message has at most 2000 characters."]})
        # A message too long with a move: refused, and the state does not move
        response = self.move(employer, "accepted", "x" * 2001)
        self.assertEqual(response.status_code, 400)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "in_progress")
        self.assertEqual(Message.objects.count(), 0)

    def test_nobody_else_reaches_the_conversation(self):
        self.move(self.login(self.employer), "in_progress", "Hello")
        others = (
            User.objects.create_user(email="c2@example.com", password=PASSWORD, role="candidate"),
            User.objects.create_user(email="e2@example.com", password=PASSWORD, role="employer"),
        )
        for user in others:
            client = self.login(user)
            self.assertEqual(client.get(self.url).status_code, 404)
            self.assertEqual(self.post(client, self.url, {"body": "Hi"}).status_code, 404)
            self.assertEqual(client.get("/api/messages/").json(), [])
        visitor = Client()
        self.assertEqual(visitor.get(self.url).status_code, 403)
        self.assertEqual(visitor.get("/api/messages/").status_code, 403)
        self.assertEqual(visitor.get("/api/messages/unread/").status_code, 403)

    def test_the_messages_go_when_the_candidate_withdraws(self):
        candidate = self.login(self.candidate)
        self.move(self.login(self.employer), "in_progress", "Hello")
        response = candidate.delete("/api/applications/%d/" % self.application.pk)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Message.objects.count(), 0)

    # ── The list and the counts ───────────────────────────────────────

    def test_the_list_of_the_conversations_and_the_unread_counts(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        # A second application, decided with a last message
        decided = self.apply(self.new_offer("Vue developer"))
        self.move(employer, "rejected", "Sorry.", application=decided)
        self.move(employer, "in_progress", "Hello")
        self.post(employer, self.url, {"body": "Are you there?"})
        # A third application without any message: no conversation
        self.apply(self.new_offer("Ops"))
        # The most recent activity first
        self.assertEqual(
            self.titles(candidate, "/api/messages/"), ["Python developer", "Vue developer"]
        )
        first = candidate.get("/api/messages/").json()[0]
        self.assertEqual((first["open"], first["unread"], first["other"]), (True, 2, "Acme"))
        self.assertEqual((first["last"]["body"], first["last"]["mine"]), ("Are you there?", False))
        self.assertEqual(self.titles(candidate, "/api/messages/?state=open"), ["Python developer"])
        self.assertEqual(self.titles(candidate, "/api/messages/?state=closed"), ["Vue developer"])
        self.assertEqual(self.unread(candidate), {"count": 3, "open": 2, "closed": 1})
        # The employer wrote them all: nothing unread on their side
        self.assertEqual(self.unread(employer), {"count": 0, "open": 0, "closed": 0})
        self.assertEqual([c["unread"] for c in employer.get("/api/messages/").json()], [0, 0])
        # Read: the count goes down
        candidate.get(self.url)
        self.assertEqual(self.unread(candidate), {"count": 1, "open": 0, "closed": 1})
