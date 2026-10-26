# backend/notifications/tests.py

"""
Notifications tests — the e-mails of the events
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check, through the API as the pages use it, that each event sends one
e-mail to the right person, in their language, with the link to the page
and without the text of a message: a new application, a withdrawal, a
move of the state (one e-mail when a message comes with it), a message
(one until it is read), an appointment proposed, answered, cancelled.
Then that nobody gets an e-mail they do not want (notifications off, demo
account, address of the seed, the seed itself), and that a failure to send
never breaks the action. The e-mails leave once the change is saved: the
tests run the callbacks of the transaction (captureOnCommitCallbacks).
"""

import json
import shutil
import tempfile
from datetime import timedelta
from io import StringIO
from unittest import mock
from zoneinfo import ZoneInfo

from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from accounts.models import User
from applications.models import JobApplication
from offers.models import JobOffer
from profiles.models import CandidateProfile, EmployerProfile

PASSWORD = "Correct-horse-9"

# Files land here during the tests, never in the media folder of the project
MEDIA = tempfile.mkdtemp(prefix="marketech-tests-")

OFFER = {
    "title": "Python developer",
    "description": "Django and Vue.",
    "city": "Geneva",
    "country": "CH",
    "contract": "permanent",
}

GENEVA = ZoneInfo("Europe/Zurich")


def pdf(name):
    return SimpleUploadedFile(name, b"%PDF-1.4 fake", content_type="application/pdf")


@override_settings(MEDIA_ROOT=MEDIA)
class NotificationTests(TestCase):
    """The e-mails of the events, through the API."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        shutil.rmtree(MEDIA, ignore_errors=True)
        cache.clear()
        # Addresses outside example.com: those of the seed get nothing
        self.candidate = User.objects.create_user(
            email="lea@candidates.test",
            password=PASSWORD,
            role="candidate",
            first_name="Léa",
            last_name="Martin",
        )
        self.employer = User.objects.create_user(
            email="marc@company.test", password=PASSWORD, role="employer"
        )
        self.profile = CandidateProfile.objects.create(user=self.candidate)
        company = EmployerProfile.objects.create(user=self.employer, company_name="Acme")
        self.offer = JobOffer.objects.create(employer=company, status="published", **OFFER)

    # ── Helpers ───────────────────────────────────────────────────────

    def login(self, user):
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        client.get("/_allauth/browser/v1/auth/session")
        client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
        return client

    def post(self, client, url, data):
        return client.post(url, data=json.dumps(data), content_type="application/json")

    def sent(self, action):
        """Run the action, the e-mails of its transaction sent, and return
        the e-mails it sent."""
        before = len(mail.outbox)
        with self.captureOnCommitCallbacks(execute=True):
            action()
        return mail.outbox[before:]

    def application(self, status="received"):
        return JobApplication.objects.create(
            offer=self.offer, candidate=self.profile, cv=pdf("cv.pdf"), status=status
        )

    def proposal(self, days=3):
        """A time in so many days, on a working day."""
        when = timezone.now() + timedelta(days=days)
        while when.astimezone(GENEVA).weekday() >= 5:
            when += timedelta(days=1)
        return when.replace(microsecond=0)

    # ── The applications ──────────────────────────────────────────────

    def test_a_new_application_tells_the_employer(self):
        client = self.login(self.candidate)
        sent = self.sent(lambda: client.post("/api/applications/", {"offer": self.offer.pk, "cv": pdf("cv.pdf")}))
        self.assertEqual(len(sent), 1)
        email = sent[0]
        self.assertEqual(email.to, ["marc@company.test"])
        # No prefix; English while the language of the account is unknown
        self.assertEqual(email.subject, "New application: Python developer")
        self.assertIn("Léa Martin has applied to your offer", email.body)
        application = JobApplication.objects.get()
        self.assertIn(f"http://testserver/employer/applications?offer={self.offer.pk}", email.body)
        self.assertIn("http://testserver/account/credentials", email.body)
        self.assertEqual(application.offer, self.offer)

    def test_the_e_mail_goes_in_the_language_of_the_account(self):
        self.employer.language = "fr"
        self.employer.save()
        client = self.login(self.candidate)
        # The candidate's interface is in English: the e-mail follows the employer
        sent = self.sent(lambda: client.post("/api/applications/", {"offer": self.offer.pk, "cv": pdf("cv.pdf")}))
        self.assertEqual(sent[0].subject, "Nouvelle candidature : Python developer")
        self.assertIn("Bonjour,", sent[0].body)
        self.assertIn("Léa Martin a postulé à votre offre « Python developer »", sent[0].body)

    def test_a_withdrawal_tells_the_employer(self):
        application = self.application()
        client = self.login(self.candidate)
        sent = self.sent(lambda: client.delete(f"/api/applications/{application.pk}/"))
        self.assertEqual([email.to for email in sent], [["marc@company.test"]])
        self.assertEqual(sent[0].subject, "Application withdrawn: Python developer")

    def test_a_move_tells_the_candidate_once_even_with_a_message(self):
        application = self.application()
        client = self.login(self.employer)
        url = f"/api/applications/{application.pk}/status/"
        sent = self.sent(lambda: self.post(client, url, {"status": "in_progress", "message": "Welcome on board."}))
        # One e-mail, not one for the move and one for the message
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0].to, ["lea@candidates.test"])
        self.assertIn("Acme has moved your application", sent[0].body)
        self.assertIn("A message comes with it.", sent[0].body)
        self.assertIn(f"http://testserver/messages/{application.pk}", sent[0].body)
        # Never the text of the message
        self.assertNotIn("Welcome on board", sent[0].body)
        sent = self.sent(lambda: self.post(client, url, {"status": "accepted"}))
        self.assertIn("Acme has accepted your application", sent[0].body)
        self.assertIn("http://testserver/candidate/applications", sent[0].body)

    # ── The messages ──────────────────────────────────────────────────

    def test_one_e_mail_until_the_messages_are_read(self):
        application = self.application(status="in_progress")
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        url = f"/api/applications/{application.pk}/messages/"
        sent = self.sent(lambda: self.post(candidate, url, {"body": "First question."}))
        self.assertEqual([email.to for email in sent], [["marc@company.test"]])
        self.assertEqual(sent[0].subject, "New message: Python developer")
        self.assertIn("Léa Martin has written to you", sent[0].body)
        self.assertNotIn("First question", sent[0].body)
        # A second message before the first is read: no e-mail
        self.assertEqual(self.sent(lambda: self.post(candidate, url, {"body": "Second."})), [])
        # Read, then a new one: an e-mail again
        employer.get(url)
        self.assertEqual(len(self.sent(lambda: self.post(candidate, url, {"body": "Third."}))), 1)
        # The other way, the company as the sender
        sent = self.sent(lambda: self.post(employer, url, {"body": "Answer."}))
        self.assertEqual(sent[0].to, ["lea@candidates.test"])
        self.assertIn("Acme has written to you", sent[0].body)

    # ── The appointments ──────────────────────────────────────────────

    def test_an_appointment_proposed_answered_and_cancelled(self):
        application = self.application(status="in_progress")
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        when = self.proposal()
        url = f"/api/applications/{application.pk}/appointments/"
        data = {"starts_at": when.isoformat(), "place": "Online", "duration": 45}
        sent = self.sent(lambda: self.post(employer, url, data))
        self.assertEqual(sent[0].to, ["lea@candidates.test"])
        self.assertEqual(sent[0].subject, "Appointment proposed: Python developer")
        local = when.astimezone(GENEVA)
        self.assertIn(f"{local:%H:%M} (Geneva time)", sent[0].body)
        self.assertIn("appointment of 45 minutes", sent[0].body)
        pk = application.appointments.get().pk
        answer = {"accept": True, "message": "Fine for me."}
        sent = self.sent(lambda: self.post(candidate, f"/api/appointments/{pk}/answer/", answer))
        self.assertEqual(sent[0].to, ["marc@company.test"])
        self.assertEqual(sent[0].subject, "Appointment accepted: Python developer")
        self.assertNotIn("Fine for me", sent[0].body)
        sent = self.sent(lambda: self.post(employer, f"/api/appointments/{pk}/cancel/", {"message": ""}))
        self.assertEqual(sent[0].to, ["lea@candidates.test"])
        self.assertEqual(sent[0].subject, "Appointment cancelled: Python developer")

    def test_the_date_reads_in_french_in_geneva(self):
        self.candidate.language = "fr"
        self.candidate.save()
        application = self.application(status="in_progress")
        when = self.proposal()
        url = f"/api/applications/{application.pk}/appointments/"
        sent = self.sent(lambda: self.post(self.login(self.employer), url, {"starts_at": when.isoformat(), "place": "Online"}))
        local = when.astimezone(GENEVA)
        self.assertIn(f" à {local:%H:%M} (heure de Genève)", sent[0].body)
        self.assertEqual(sent[0].subject, "Rendez-vous proposé : Python developer")

    # ── Nobody gets an e-mail they do not want ────────────────────────

    def test_nothing_for_a_user_without_notifications_a_demo_or_the_seed(self):
        client = self.login(self.candidate)
        apply = lambda: client.post("/api/applications/", {"offer": self.offer.pk, "cv": pdf("cv.pdf")})  # noqa: E731
        self.employer.notify_by_email = False
        self.employer.save()
        self.assertEqual(self.sent(apply), [])
        JobApplication.objects.all().delete()
        self.employer.notify_by_email = True
        self.employer.is_demo = True
        self.employer.save()
        self.assertEqual(self.sent(apply), [])
        JobApplication.objects.all().delete()
        self.employer.is_demo = False
        self.employer.email = "marc@example.com"
        self.employer.save()
        self.assertEqual(self.sent(apply), [])

    @override_settings(DEBUG=True)
    def test_the_seed_sends_nothing(self):
        self.assertEqual(self.sent(lambda: call_command("seed_demo", stdout=StringIO())), [])

    def test_a_failure_to_send_never_breaks_the_action(self):
        client = self.login(self.candidate)
        with (
            mock.patch("notifications.send.send_mail", side_effect=OSError("refused")),
            self.assertLogs("notifications.send", level="WARNING") as logs,
        ):
            with self.captureOnCommitCallbacks(execute=True):
                response = client.post("/api/applications/", {"offer": self.offer.pk, "cv": pdf("cv.pdf")})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(JobApplication.objects.count(), 1)
        # The event and the number of the account, never the address
        self.assertIn(f"application_received to user {self.employer.pk} not sent (OSError)", logs.output[0])
        self.assertNotIn("company.test", logs.output[0])
