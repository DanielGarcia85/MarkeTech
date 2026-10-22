# backend/appointments/tests.py

"""
Appointments tests — the appointments and their rules
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the model of the appointments: they read in the order they take
place and end after their length; the database refuses a second pending
appointment on the same application, an appointment without a place, an
answer without a message and a length not offered; an appointment goes
with its application, whether withdrawn or deleted with its offer or an
account; the participant who has news follows from the state; a pending
appointment expires when its time has come or its application is decided.
"""

import shutil
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone

from accounts.models import User
from applications.models import JobApplication
from offers.models import JobOffer
from profiles.models import CandidateProfile, EmployerProfile

from .models import Appointment

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
class AppointmentModelTests(TestCase):
    """The appointments of an application."""

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
        self.tomorrow = timezone.now() + timedelta(days=1)

    def propose(self, days=1, **fields):
        fields = {"place": "Rue du Rhône 1, Genève", **fields}
        return Appointment.objects.create(
            application=self.application,
            starts_at=timezone.now() + timedelta(days=days),
            **fields,
        )

    def test_appointments_read_in_the_order_they_take_place(self):
        later = self.propose(days=5, status="declined", response="I am not free.")
        sooner = self.propose(days=2)
        self.assertEqual(list(self.application.appointments.all()), [sooner, later])
        # One hour unless said otherwise, and its end follows
        self.assertEqual(sooner.duration, 60)
        self.assertEqual(sooner.ends_at - sooner.starts_at, timedelta(hours=1))

    def test_one_pending_appointment_per_application(self):
        first = self.propose()
        # atomic() keeps the test transaction usable after the refusal
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.propose(days=2)
        # Once the first is answered, another may be proposed
        first.status = "accepted"
        first.response = "Fine for me."
        first.save()
        self.propose(days=3)
        self.assertEqual(Appointment.objects.count(), 2)

    def test_the_database_refuses_an_incomplete_appointment(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.propose(place="")
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.propose(status="declined", response="")
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.propose(duration=20)
        # A cancellation may come without a word
        self.propose(status="cancelled")
        self.assertEqual(Appointment.objects.count(), 1)

    def test_the_appointments_go_with_their_application(self):
        self.propose()
        self.application.delete()
        self.assertEqual(Appointment.objects.count(), 0)

    def test_the_appointments_go_with_the_offer_or_an_account(self):
        self.propose()
        self.offer.delete()
        self.assertEqual(Appointment.objects.count(), 0)
        offer = JobOffer.objects.create(
            employer=EmployerProfile.objects.get(user=self.employer), status="published", **OFFER
        )
        self.application = JobApplication.objects.create(
            offer=offer,
            candidate=CandidateProfile.objects.get(user=self.candidate),
            cv=SimpleUploadedFile("cv.pdf", b"%PDF-1.4 fake"),
            status="in_progress",
        )
        self.propose()
        self.candidate.delete()
        self.assertEqual(Appointment.objects.count(), 0)

    def test_who_has_news_follows_from_the_state(self):
        appointment = self.propose()
        self.assertEqual(appointment.recipient, "candidate")
        appointment.status = "accepted"
        self.assertEqual(appointment.recipient, "employer")
        appointment.status = "declined"
        self.assertEqual(appointment.recipient, "employer")
        appointment.status = "cancelled"
        self.assertEqual(appointment.recipient, "candidate")

    def test_a_pending_appointment_expires(self):
        appointment = self.propose()
        self.assertFalse(appointment.is_expired())
        # Its time has come
        self.assertTrue(appointment.is_expired(now=appointment.starts_at))
        # Its application decided
        self.application.status = "rejected"
        self.application.save()
        appointment.refresh_from_db()
        self.assertTrue(appointment.is_expired())
        # An answered appointment never expires
        appointment.status = "accepted"
        appointment.response = "Fine for me."
        self.assertFalse(appointment.is_expired())
