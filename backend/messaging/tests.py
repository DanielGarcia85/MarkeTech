# backend/messaging/tests.py

"""
Messaging tests — the messages and their conversation
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the model of the messages: a message belongs to an application,
reads in the order it was sent, is unread until the other participant
opens it, cannot be empty, and goes with its application, whether the
application is withdrawn or deleted with its offer or with an account.
"""

import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings

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
