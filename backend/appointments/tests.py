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
Then the API as the pages will use it: only the employer proposes, while
the application is in progress, one pending at a time; only the candidate
answers, once, with a message; only the employer cancels, before the
appointment; nobody else reaches them; what is news, marked seen once
read; the appointments of a user over a period; an accepted appointment
to come as a calendar file, its texts escaped and its lines folded as
the format asks.
"""

import json
import shutil
import tempfile
from datetime import UTC, timedelta
from zoneinfo import ZoneInfo

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from accounts.models import User
from applications.models import JobApplication
from offers.models import JobOffer
from profiles.models import CandidateProfile, EmployerProfile

from .ics import fold
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


@override_settings(MEDIA_ROOT=MEDIA)
class AppointmentApiTests(TestCase):
    """The appointments of an application through the API."""

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
        self.stranger = User.objects.create_user(
            email="other@example.com", password=PASSWORD, role="employer"
        )
        profile = CandidateProfile.objects.create(user=self.candidate)
        company = EmployerProfile.objects.create(user=self.employer, company_name="Acme")
        EmployerProfile.objects.create(user=self.stranger, company_name="Other")
        offer = JobOffer.objects.create(employer=company, status="published", **OFFER)
        self.application = JobApplication.objects.create(
            offer=offer,
            candidate=profile,
            cv=SimpleUploadedFile("cv.pdf", b"%PDF-1.4 fake"),
            status="in_progress",
        )
        self.url = "/api/applications/%d/appointments/" % self.application.pk

    # ── Helpers ───────────────────────────────────────────────────────

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

    def proposal(self, days=2, **fields):
        """What the employer sends: a time in so many days, and a place."""
        when = (timezone.now() + timedelta(days=days)).isoformat()
        return {"starts_at": when, "place": "Rue du Rhône 1, Genève", **fields}

    def propose(self, client, days=2, **fields):
        return self.post(client, self.url, self.proposal(days, **fields))

    def answer(self, client, pk, accept=True, message="Fine for me."):
        url = "/api/appointments/%d/answer/" % pk
        return self.post(client, url, {"accept": accept, "message": message})

    def cancel(self, client, pk, message=""):
        return self.post(client, "/api/appointments/%d/cancel/" % pk, {"message": message})

    def unseen(self, client):
        return client.get("/api/appointments/unseen/").json()

    # ── Proposing ─────────────────────────────────────────────────────

    def test_only_the_employer_proposes_while_in_progress(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        self.assertEqual(self.propose(candidate).status_code, 403)
        # Someone outside the application does not learn it exists
        self.assertEqual(self.propose(self.login(self.stranger)).status_code, 404)
        self.assertEqual(self.login(self.stranger).get(self.url).status_code, 404)
        # Not taken up, or decided: no proposal
        for state in ("received", "accepted"):
            JobApplication.objects.filter(pk=self.application.pk).update(status=state)
            response = self.propose(employer)
            self.assertEqual(response.status_code, 400)
        JobApplication.objects.filter(pk=self.application.pk).update(status="in_progress")
        response = self.propose(employer, duration=45, note="  Bring your portfolio.  ")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(
            (data["state"], data["duration"], data["note"]),
            ("pending", 45, "Bring your portfolio."),
        )
        self.assertEqual(
            data["about"], {"offer": "Python developer", "company": "Acme", "other": "Léa Martin"}
        )
        listed = candidate.get(self.url).json()
        self.assertEqual(listed[0]["about"]["other"], "Acme")

    def test_what_the_employer_proposes_is_checked(self):
        employer = self.login(self.employer)
        errors = self.propose(employer, days=-1).json()
        self.assertEqual(errors, {"starts_at": ["An appointment is proposed in the future."]})
        errors = self.propose(employer, days=400).json()
        self.assertEqual(errors, {"starts_at": ["An appointment is proposed within a year."]})
        errors = self.propose(employer, place="   ").json()
        self.assertEqual(errors, {"place": ["Say where, or how, you will meet."]})
        errors = self.propose(employer, duration=20).json()
        self.assertEqual(errors, {"duration": ["This length is not offered."]})
        errors = self.post(employer, self.url, {"place": "Online"}).json()
        self.assertEqual(errors, {"starts_at": ["Give a date and a time."]})
        self.assertEqual(Appointment.objects.count(), 0)

    def test_the_refusals_speak_the_language_of_the_interface(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        for client in (candidate, employer):
            client.defaults["HTTP_ACCEPT_LANGUAGE"] = "fr"
        errors = self.propose(employer, days=400, place="   ").json()
        self.assertEqual(
            errors,
            {
                "starts_at": ["Un rendez-vous se propose au plus un an à l'avance."],
                "place": ["Indiquez où, ou comment, vous vous rencontrerez."],
            },
        )
        errors = self.propose(employer, place="x" * 201).json()
        self.assertEqual(errors, {"place": ["Un lieu compte au plus 200 caractères."]})
        self.assertEqual(
            self.propose(candidate).json(), {"detail": "Seul l'employeur propose un rendez-vous."}
        )
        pk = self.propose(employer).json()["id"]
        errors = self.answer(candidate, pk, message="").json()
        self.assertEqual(errors, {"message": ["Écrivez un message avec votre réponse."]})

    def test_one_pending_proposal_at_a_time(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        first = self.propose(employer).json()
        response = self.propose(employer, days=3)
        self.assertEqual(
            response.json(),
            {"non_field_errors": ["This application already has a pending appointment."]},
        )
        # Answered: a second meeting may be proposed
        self.answer(candidate, first["id"])
        self.assertEqual(self.propose(employer, days=9).status_code, 201)
        # Left without answer after its time: a new proposal replaces it
        past = timezone.now() - timedelta(hours=1)
        Appointment.objects.filter(status="pending").update(starts_at=past)
        self.assertEqual(self.propose(employer, days=10).status_code, 201)
        states = [a["state"] for a in employer.get(self.url).json()]
        self.assertEqual(states, ["cancelled", "accepted", "pending"])

    # ── Answering and cancelling ──────────────────────────────────────

    def test_the_candidate_answers_once_with_a_message(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        pk = self.propose(employer).json()["id"]
        self.assertEqual(self.answer(employer, pk).status_code, 403)
        self.assertEqual(self.answer(self.login(self.stranger), pk).status_code, 404)
        errors = self.answer(candidate, pk, message="  ").json()
        self.assertEqual(errors, {"message": ["Write a message with your answer."]})
        response = self.answer(candidate, pk, accept=False, message="  I am abroad that week.  ")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual((data["state"], data["response"]), ("declined", "I am abroad that week."))
        self.assertIsNotNone(data["answered_at"])
        # Once only
        self.assertEqual(self.answer(candidate, pk).status_code, 400)

    def test_an_expired_appointment_is_not_answered(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        pk = self.propose(employer).json()["id"]
        # The application decided before the answer
        JobApplication.objects.filter(pk=self.application.pk).update(status="rejected")
        self.assertEqual(candidate.get(self.url).json()[0]["state"], "expired")
        response = self.answer(candidate, pk)
        self.assertEqual(
            response.json(), {"non_field_errors": ["This appointment can no longer be answered."]}
        )
        # Moved back in progress, and its time not come: it can be answered again
        JobApplication.objects.filter(pk=self.application.pk).update(status="in_progress")
        self.assertEqual(self.answer(candidate, pk).status_code, 200)

    def test_the_employer_cancels_before_the_appointment(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        pk = self.propose(employer).json()["id"]
        self.assertEqual(self.cancel(candidate, pk).status_code, 403)
        self.answer(candidate, pk)
        response = self.cancel(employer, pk, "  Our office is closed that day.  ")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            (data["state"], data["response"]), ("cancelled", "Our office is closed that day.")
        )
        self.assertEqual(self.cancel(employer, pk).status_code, 400)
        # Accepted and past: it took place, nothing to cancel
        pk = self.propose(employer, days=3).json()["id"]
        self.answer(candidate, pk)
        Appointment.objects.filter(pk=pk).update(starts_at=timezone.now() - timedelta(days=1))
        response = self.cancel(employer, pk)
        self.assertEqual(
            response.json(), {"non_field_errors": ["This appointment can no longer be cancelled."]}
        )

    # ── News and the calendar ─────────────────────────────────────────

    def test_each_change_is_news_for_the_other_side(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        pk = self.propose(employer).json()["id"]
        key = str(self.application.pk)
        self.assertEqual(self.unseen(candidate), {"count": 1, "applications": {key: 1}})
        self.assertEqual(self.unseen(employer), {"count": 0, "applications": {}})
        # Read once: new in that answer, seen afterwards
        self.assertTrue(candidate.get(self.url).json()[0]["new"])
        self.assertFalse(candidate.get(self.url).json()[0]["new"])
        self.assertEqual(self.unseen(candidate)["count"], 0)
        # The answer is news for the employer, read from the calendar
        self.answer(candidate, pk)
        self.assertEqual(self.unseen(employer)["count"], 1)
        self.assertTrue(employer.get("/api/appointments/").json()[0]["new"])
        self.assertEqual(self.unseen(employer)["count"], 0)
        # The cancellation, news for the candidate again
        self.cancel(employer, pk)
        self.assertEqual(self.unseen(candidate)["count"], 1)

    def test_my_appointments_over_a_period(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        first = self.propose(employer, days=2).json()
        self.answer(candidate, first["id"])
        self.propose(employer, days=20)
        self.assertEqual(len(candidate.get("/api/appointments/").json()), 2)
        start = timezone.now().date().isoformat()
        end = (timezone.now() + timedelta(days=7)).isoformat()
        week = employer.get("/api/appointments/", {"start": start, "end": end}).json()
        self.assertEqual([a["id"] for a in week], [first["id"]])
        response = employer.get("/api/appointments/", {"start": "next monday"})
        self.assertEqual(response.json(), {"start": ["Give a date or a time."]})
        # Somebody else's appointments are not theirs
        self.assertEqual(self.login(self.stranger).get("/api/appointments/").json(), [])

    # ── The calendar file ─────────────────────────────────────────────

    def calendar(self, client, pk):
        return client.get("/api/appointments/%d/calendar/" % pk)

    def test_an_accepted_appointment_to_come_is_a_calendar_file(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        note = "Bring your laptop, your CV; and a smile.\nSecond floor."
        pk = self.propose(employer, note=note, duration=90).json()["id"]
        # Pending: not in an agenda yet
        self.assertEqual(self.calendar(candidate, pk).status_code, 404)
        self.answer(candidate, pk)
        response = self.calendar(candidate, pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/calendar; charset=utf-8")
        appointment = Appointment.objects.get(pk=pk)
        day = timezone.localtime(appointment.starts_at, ZoneInfo("Europe/Zurich")).date()
        self.assertEqual(
            response["Content-Disposition"], f'attachment; filename="rendez-vous-{day}.ics"'
        )
        body = response.content.decode()
        # Every line ended by CRLF and never longer than 75 bytes
        lines = body.split("\r\n")
        self.assertEqual(lines[-1], "")
        self.assertTrue(all(len(line.encode()) <= 75 for line in lines))
        unfolded = body.replace("\r\n ", "").split("\r\n")
        self.assertEqual(unfolded[:2], ["BEGIN:VCALENDAR", "VERSION:2.0"])
        self.assertIn("UID:appointment-%d@testserver" % pk, unfolded)
        start = appointment.starts_at.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
        end = appointment.ends_at.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
        self.assertIn("DTSTART:" + start, unfolded)
        self.assertIn("DTEND:" + end, unfolded)
        self.assertIn("SUMMARY:Python developer · Acme", unfolded)
        self.assertIn("LOCATION:Rue du Rhône 1\\, Genève", unfolded)
        self.assertIn(
            "DESCRIPTION:Bring your laptop\\, your CV\\; and a smile.\\nSecond floor.", unfolded
        )
        # The employer gets the candidate's name as the other participant
        body = self.calendar(employer, pk).content.decode()
        self.assertIn("SUMMARY:Python developer · Léa Martin", body.replace("\r\n ", ""))

    def test_no_calendar_file_for_another_appointment_or_another_user(self):
        candidate, employer = self.login(self.candidate), self.login(self.employer)
        pk = self.propose(employer).json()["id"]
        self.answer(candidate, pk)
        self.assertEqual(self.calendar(self.login(self.stranger), pk).status_code, 404)
        # Taken place already
        Appointment.objects.filter(pk=pk).update(starts_at=timezone.now() - timedelta(hours=2))
        self.assertEqual(self.calendar(candidate, pk).status_code, 404)
        # Cancelled
        pk = self.propose(employer, days=5).json()["id"]
        self.answer(candidate, pk)
        self.cancel(employer, pk)
        self.assertEqual(self.calendar(candidate, pk).status_code, 404)

    def test_a_long_line_is_folded_between_characters(self):
        line = "SUMMARY:" + "é" * 80
        folded = fold(line)
        parts = folded.split("\r\n")
        self.assertTrue(all(len(part.encode()) <= 75 for part in parts))
        self.assertTrue(all(part.startswith(" ") for part in parts[1:]))
        self.assertEqual(folded.replace("\r\n ", ""), line)
