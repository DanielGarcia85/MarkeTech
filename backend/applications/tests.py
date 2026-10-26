# backend/applications/tests.py

"""
Application tests — the job applications and their API
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the models of the applications: the history is written by the model
at the creation and at each change of status, a candidate applies once per
offer, the files land in the folder of the application and leave the disk
with it, whether the application is deleted itself or with its offer. Then
the API as the frontend will use it: a candidate applies to a published
offer with a CV sent or copied from the profile, a letter and documents of
the profile, follows and withdraws their applications; an employer reads
the applications to their offers and moves their state; the files are
served to both and to nobody else; and the offers that received
applications are counted for their employer and cannot be deleted. Last,
the news: an application arriving for the employer, a move of its state
for the candidate, flagged once in the list, then seen, and counted for
the side bar until then.
"""

import json
import os
import shutil
import tempfile

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings

from accounts.models import User
from offers.models import JobOffer
from profiles.models import CandidateDocument, CandidateProfile, EmployerProfile

from .models import Attachment, JobApplication

PASSWORD = "Correct-horse-9"
PDF = b"%PDF-1.4 fake"

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


def pdf(name, content=PDF):
    """A file as the API receives it, with a PDF content."""
    return SimpleUploadedFile(name, content)


def on_disk(name):
    """Whether the file of that name is in MEDIA_ROOT."""
    return os.path.exists(os.path.join(MEDIA, name))


class MediaTestCase(TestCase):
    """A test case whose files go to a temporary folder, emptied before
    each test (a name already taken would get a suffix, and the paths are
    checked in full) and removed at the end."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        shutil.rmtree(MEDIA, ignore_errors=True)


# ── The models ────────────────────────────────────────────────────────


@override_settings(MEDIA_ROOT=MEDIA)
class ApplicationModelTests(MediaTestCase):
    """The application, its history, its uniqueness and its files."""

    def setUp(self):
        super().setUp()
        candidate = User.objects.create_user(
            email="cand@example.com", password=PASSWORD, role="candidate"
        )
        employer = User.objects.create_user(
            email="emp@example.com", password=PASSWORD, role="employer"
        )
        self.candidate = CandidateProfile.objects.create(user=candidate)
        company = EmployerProfile.objects.create(user=employer, company_name="Acme")
        self.offer = JobOffer.objects.create(employer=company, status="published", **OFFER)

    def apply(self, **fields):
        """A new application of the candidate to the offer, with a CV."""
        fields.setdefault("cv", pdf("cv.pdf"))
        return JobApplication.objects.create(offer=self.offer, candidate=self.candidate, **fields)

    def test_the_history_follows_the_status(self):
        application = self.apply()
        self.assertEqual(application.status, "received")
        self.assertEqual([c.status for c in application.history.all()], ["received"])
        # Loaded again, as a view or the admin site would, then changed
        application = JobApplication.objects.get(pk=application.pk)
        application.status = "in_progress"
        application.save()
        self.assertEqual(
            [c.status for c in application.history.all()], ["received", "in_progress"]
        )
        # Saved without a change of status: nothing added
        application.save()
        application = JobApplication.objects.get(pk=application.pk)
        application.cover_letter = pdf("letter.pdf")
        application.save()
        self.assertEqual(application.history.count(), 2)

    def test_a_candidate_applies_once_per_offer(self):
        self.apply()
        # The database refuses the second one; atomic() keeps the test
        # transaction usable after the error
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.apply()
        self.assertEqual(JobApplication.objects.count(), 1)

    def test_the_files_land_in_the_folder_of_the_application(self):
        application = self.apply(cover_letter=pdf("letter.pdf"))
        attachment = Attachment.objects.create(application=application, file=pdf("diploma.pdf"))
        folder = "applications/%d/%d/" % (self.candidate.user_id, self.offer.pk)
        self.assertEqual(application.cv.name, folder + "cv.pdf")
        self.assertEqual(application.cover_letter.name, folder + "letter.pdf")
        self.assertEqual(attachment.file.name, folder + "documents/diploma.pdf")
        self.assertTrue(on_disk(application.cv.name))
        self.assertTrue(on_disk(attachment.file.name))

    def test_the_files_go_with_the_application(self):
        application = self.apply(cover_letter=pdf("letter.pdf"))
        attachment = Attachment.objects.create(application=application, file=pdf("diploma.pdf"))
        # The names, before the deletion empties the fields
        names = [application.cv.name, application.cover_letter.name, attachment.file.name]
        self.assertTrue(all(on_disk(name) for name in names))
        application.delete()
        self.assertFalse(any(on_disk(name) for name in names))
        self.assertEqual(Attachment.objects.count(), 0)

    def test_the_files_go_with_the_offer(self):
        application = self.apply()
        attachment = Attachment.objects.create(application=application, file=pdf("diploma.pdf"))
        names = [application.cv.name, attachment.file.name]
        # The cascade of the offer: no delete() called on the application
        self.offer.delete()
        self.assertEqual(JobApplication.objects.count(), 0)
        self.assertFalse(any(on_disk(name) for name in names))


# ── The API ───────────────────────────────────────────────────────────


@override_settings(MEDIA_ROOT=MEDIA)
class ApplicationApiTests(MediaTestCase):
    """Applying, following, withdrawing; reading and moving as an employer;
    the files; the offers that received applications."""

    def setUp(self):
        super().setUp()
        # The counts of the write limits live in the cache: none left by
        # another test, whose account could have had the same number
        cache.clear()
        self.candidate = User.objects.create_user(
            email="cand@example.com",
            password=PASSWORD,
            role="candidate",
            first_name="Marie",
            last_name="Dupont",
        )
        self.other_candidate = User.objects.create_user(
            email="cand2@example.com", password=PASSWORD, role="candidate"
        )
        self.employer = User.objects.create_user(
            email="emp@example.com", password=PASSWORD, role="employer"
        )
        self.other_employer = User.objects.create_user(
            email="emp2@example.com", password=PASSWORD, role="employer"
        )
        # Profiles as the profile pages would have made them: the candidate
        # with a CV and two documents, the employers with a company
        self.profile = CandidateProfile.objects.create(
            user=self.candidate, phone="+41 22 000 00 00", city="Geneva", cv=pdf("profile-cv.pdf")
        )
        self.diploma = CandidateDocument.objects.create(candidate=self.profile, file=pdf("diploma.pdf"))
        self.letter = CandidateDocument.objects.create(candidate=self.profile, file=pdf("reference.pdf"))
        CandidateProfile.objects.create(user=self.other_candidate)
        self.company = EmployerProfile.objects.create(user=self.employer, company_name="Acme")
        self.other_company = EmployerProfile.objects.create(
            user=self.other_employer, company_name="Globex"
        )
        self.offer = JobOffer.objects.create(employer=self.company, status="published", **OFFER)

    # ── Helpers ───────────────────────────────────────────────────────

    def login(self, user):
        """A client logged in as the user, with the CSRF token a browser
        would send back (enforced, as in the other API tests)."""
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        client.get("/_allauth/browser/v1/auth/session")
        client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
        return client

    def post(self, client, url, data=None):
        return client.post(url, data=json.dumps(data or {}), content_type="application/json")

    def apply(self, client=None, offer=None, **fields):
        """POST the form of an application, a fresh CV file unless said
        otherwise; multipart, as the browser sends files."""
        data = {"offer": (offer or self.offer).pk, **fields}
        if "cv" not in data and not data.get("use_profile_cv"):
            data["cv"] = pdf("cv.pdf")
        return (client or self.login(self.candidate)).post("/api/applications/", data)

    def application(self, candidate=None, offer=None, status="received"):
        """An application in the database, with a CV."""
        profile = CandidateProfile.objects.get(user=candidate or self.candidate)
        application = JobApplication.objects.create(
            offer=offer or self.offer, candidate=profile, cv=pdf("cv.pdf")
        )
        if status != "received":
            application.status = status
            application.save()
        return application

    def status_of(self, client, url):
        """Status of a GET on a file URL, the file closed at once: a served
        file stays open until its response is closed, and Windows refuses
        to delete an open file. Read to its end, the file is closed by the
        test client itself. Never response.close(): it sends the signal of
        a finished request, which closes the database connection of the
        test; SQLite in memory ignores it, PostgreSQL refuses every query
        after it (found on 22.10.2026)."""
        response = client.get(url)
        if response.streaming:
            b"".join(response.streaming_content)
        return response.status_code

    # ── Applying ──────────────────────────────────────────────────────

    def test_a_candidate_applies_with_a_cv_a_letter_and_documents(self):
        response = self.apply(
            cover_letter=pdf("letter.pdf"), documents=[self.diploma.pk, self.letter.pk]
        )
        self.assertEqual(response.status_code, 201, response.content)
        data = response.json()
        self.assertEqual(data["status"], "received")
        self.assertEqual([c["status"] for c in data["history"]], ["received"])
        self.assertEqual(data["offer"]["title"], "Python developer")
        self.assertEqual(data["offer"]["company"], {"name": "Acme"})
        self.assertEqual(data["candidate"]["first_name"], "Marie")
        self.assertEqual(data["candidate"]["email"], "cand@example.com")
        self.assertEqual(data["candidate"]["phone"], "+41 22 000 00 00")
        self.assertNotIn("photo", data["candidate"])
        self.assertEqual(data["cv"]["name"], "cv.pdf")
        self.assertEqual(data["cv"]["url"], "/api/applications/%d/cv/" % data["id"])
        self.assertEqual(data["cover_letter"]["name"], "letter.pdf")
        self.assertEqual([a["name"] for a in data["attachments"]], ["diploma.pdf", "reference.pdf"])
        # The documents are copies in the folder of the application
        application = JobApplication.objects.get(pk=data["id"])
        folder = "applications/%d/%d/" % (self.candidate.pk, self.offer.pk)
        self.assertEqual(application.cv.name, folder + "cv.pdf")
        self.assertEqual(
            [a.file.name for a in application.attachments.all()],
            [folder + "documents/diploma.pdf", folder + "documents/reference.pdf"],
        )

    def test_the_cv_of_the_profile_can_be_copied(self):
        response = self.apply(use_profile_cv=True)
        self.assertEqual(response.status_code, 201, response.content)
        application = JobApplication.objects.get(pk=response.json()["id"])
        self.assertEqual(
            application.cv.name,
            "applications/%d/%d/profile-cv.pdf" % (self.candidate.pk, self.offer.pk),
        )
        # A copy: the profile loses its CV, the application keeps its own
        self.profile.cv.delete()
        self.assertTrue(on_disk(application.cv.name))
        self.assertEqual(response.json()["cover_letter"], None)
        self.assertEqual(response.json()["attachments"], [])

    def test_applying_needs_a_cv_one_way_or_the_other(self):
        client = self.login(self.candidate)
        response = client.post("/api/applications/", {"offer": self.offer.pk})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"cv": ["A CV is required."]})
        self.profile.cv.delete()
        response = client.post("/api/applications/", {"offer": self.offer.pk, "use_profile_cv": True})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"cv": ["Your profile has no CV."]})
        # The same refusals in the language of the interface
        response = client.post(
            "/api/applications/", {"offer": self.offer.pk}, HTTP_ACCEPT_LANGUAGE="fr"
        )
        self.assertEqual(response.json(), {"cv": ["Un CV est obligatoire."]})
        response = client.post(
            "/api/applications/",
            {"offer": self.offer.pk, "use_profile_cv": True},
            HTTP_ACCEPT_LANGUAGE="fr",
        )
        self.assertEqual(response.json(), {"cv": ["Votre profil n'a pas de CV."]})
        # The rules of the files hold here too
        response = self.apply(client, cv=SimpleUploadedFile("cv.exe", b"MZ"))
        self.assertEqual(response.status_code, 400)
        self.assertIn("cv", response.json())
        self.assertEqual(JobApplication.objects.count(), 0)

    def test_applying_is_refused_twice_and_outside_the_published_offers(self):
        client = self.login(self.candidate)
        self.assertEqual(self.apply(client).status_code, 201)
        response = self.apply(client)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"non_field_errors": ["You have already applied to this offer."]}
        )
        for offer in (
            JobOffer.objects.create(employer=self.company, status="draft", **OFFER),
            JobOffer.objects.create(employer=self.company, status="closed", **OFFER),
        ):
            response = self.apply(client, offer=offer)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), {"offer": ["This offer is not open to applications."]})
        # No such offer: the same answer
        response = client.post("/api/applications/", {"offer": 9999, "cv": pdf("cv.pdf")})
        self.assertEqual(response.json(), {"offer": ["This offer is not open to applications."]})

    def test_only_the_documents_of_the_candidate_can_be_joined(self):
        other = CandidateDocument.objects.create(
            candidate=CandidateProfile.objects.get(user=self.other_candidate), file=pdf("x.pdf")
        )
        response = self.apply(documents=[self.diploma.pk, other.pk])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"documents": ["Unknown document."]})
        self.assertEqual(JobApplication.objects.count(), 0)

    def test_only_a_candidate_applies(self):
        self.assertEqual(self.apply(self.login(self.employer)).status_code, 403)
        self.assertEqual(Client().post("/api/applications/", {"offer": self.offer.pk}).status_code, 403)

    # ── Following, as a candidate ─────────────────────────────────────

    def test_a_candidate_sees_their_own_applications_only(self):
        mine = self.application()
        other_offer = JobOffer.objects.create(employer=self.other_company, status="published", **OFFER)
        self.application(offer=other_offer)
        theirs = self.application(candidate=self.other_candidate)
        client = self.login(self.candidate)
        response = client.get("/api/applications/")
        self.assertEqual(response.status_code, 200)
        # Newest first, mine only
        self.assertEqual([a["offer"]["company"]["name"] for a in response.json()], ["Globex", "Acme"])
        response = client.get("/api/applications/?offer=%d" % self.offer.pk)
        self.assertEqual([a["id"] for a in response.json()], [mine.pk])
        self.assertEqual(client.get("/api/applications/%d/" % mine.pk).status_code, 200)
        self.assertEqual(client.get("/api/applications/%d/" % theirs.pk).status_code, 404)
        self.assertEqual(Client().get("/api/applications/").status_code, 403)

    def test_a_candidate_withdraws_until_the_employer_decides(self):
        client = self.login(self.candidate)
        application = self.application()
        Attachment.objects.create(application=application, file=pdf("diploma.pdf"))
        names = [application.cv.name, application.attachments.first().file.name]
        response = client.delete("/api/applications/%d/" % application.pk)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(JobApplication.objects.count(), 0)
        self.assertFalse(any(on_disk(name) for name in names))
        for status in ("accepted", "rejected"):
            offer = JobOffer.objects.create(employer=self.company, status="published", **OFFER)
            decided = self.application(offer=offer, status=status)
            response = client.delete("/api/applications/%d/" % decided.pk)
            self.assertEqual(response.status_code, 400)
            self.assertIn("non_field_errors", response.json())
        self.assertEqual(JobApplication.objects.count(), 2)
        # Someone else's: not found; an employer: not allowed
        theirs = self.application(candidate=self.other_candidate)
        self.assertEqual(client.delete("/api/applications/%d/" % theirs.pk).status_code, 404)
        employer = self.login(self.employer)
        self.assertEqual(employer.delete("/api/applications/%d/" % theirs.pk).status_code, 403)

    # ── Reading and moving, as an employer ────────────────────────────

    def test_an_employer_sees_the_applications_to_their_offers_only(self):
        mine = self.application()
        self.application(candidate=self.other_candidate, status="in_progress")
        other_offer = JobOffer.objects.create(employer=self.other_company, status="published", **OFFER)
        theirs = self.application(offer=other_offer)
        client = self.login(self.employer)
        response = client.get("/api/applications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        response = client.get("/api/applications/?offer=%d&status=received" % self.offer.pk)
        self.assertEqual([a["id"] for a in response.json()], [mine.pk])
        self.assertEqual(response.json()[0]["candidate"]["last_name"], "Dupont")
        self.assertEqual(client.get("/api/applications/?offer=%d" % other_offer.pk).json(), [])
        self.assertEqual(client.get("/api/applications/%d/" % theirs.pk).status_code, 404)

    def test_an_employer_moves_the_status_and_the_history_follows(self):
        application = self.application()
        client = self.login(self.employer)
        url = "/api/applications/%d/status/" % application.pk
        response = self.post(client, url, {"status": "in_progress"})
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["status"], "in_progress")
        response = self.post(client, url, {"status": "in_progress"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(), {"non_field_errors": ["The application is already in this status."]}
        )
        for bad in ("received", "done", None):
            response = self.post(client, url, {"status": bad})
            self.assertEqual(response.status_code, 400)
            self.assertIn("status", response.json())
        # Back from a decision is allowed: the history tells
        self.assertEqual(self.post(client, url, {"status": "rejected"}).status_code, 200)
        response = self.post(client, url, {"status": "accepted"})
        self.assertEqual(
            [c["status"] for c in response.json()["history"]],
            ["received", "in_progress", "rejected", "accepted"],
        )
        # Another employer: not found; a candidate: not allowed
        other = self.login(self.other_employer)
        self.assertEqual(self.post(other, url, {"status": "rejected"}).status_code, 404)
        candidate = self.login(self.candidate)
        self.assertEqual(self.post(candidate, url, {"status": "rejected"}).status_code, 403)

    # ── The files ─────────────────────────────────────────────────────

    def test_the_files_are_served_to_the_two_sides_only(self):
        response = self.apply(cover_letter=pdf("letter.pdf"), documents=[self.diploma.pk])
        data = response.json()
        attachment = data["attachments"][0]
        urls = [data["cv"]["url"], data["cover_letter"]["url"], attachment["url"]]
        expected = "/api/applications/%d/attachments/%d/" % (data["id"], attachment["id"])
        self.assertEqual(urls[2], expected)
        for user in (self.candidate, self.employer):
            client = self.login(user)
            self.assertEqual([self.status_of(client, url) for url in urls], [200, 200, 200])
        response = self.login(self.candidate).get(urls[0])
        # Read to its end: closed by the test client, as status_of says
        self.assertEqual(b"".join(response.streaming_content), PDF)
        self.assertIn("cv.pdf", response["Content-Disposition"])
        for user in (self.other_candidate, self.other_employer):
            client = self.login(user)
            self.assertEqual([self.status_of(client, url) for url in urls], [404, 404, 404])
        self.assertEqual([self.status_of(Client(), url) for url in urls], [403, 403, 403])
        # Not under the public media URL either
        path = JobApplication.objects.get(pk=data["id"]).cv.name
        self.assertEqual(self.status_of(self.login(self.candidate), "/api/files/" + path), 404)

    def test_a_missing_letter_or_attachment_is_not_found(self):
        application = self.application()
        client = self.login(self.candidate)
        self.assertEqual(self.status_of(client, "/api/applications/%d/cover-letter/" % application.pk), 404)
        self.assertEqual(self.status_of(client, "/api/applications/%d/attachments/1/" % application.pk), 404)

    # ── The offers that received applications ─────────────────────────

    def test_the_employer_sees_how_many_applied_and_cannot_delete_the_offer(self):
        self.application()
        self.application(candidate=self.other_candidate)
        empty = JobOffer.objects.create(employer=self.company, status="published", **OFFER)
        client = self.login(self.employer)
        counts = {o["id"]: o["applications_count"] for o in client.get("/api/offers/mine/").json()}
        self.assertEqual(counts, {self.offer.pk: 2, empty.pk: 0})
        # The detail of the offer: the count for its employer, who sees it is
        # theirs; neither for the public nor for another employer
        detail = client.get("/api/offers/%d/" % self.offer.pk).json()
        self.assertEqual((detail["mine"], detail["applications_count"]), (True, 2))
        for other in (Client(), self.login(self.other_employer), self.login(self.candidate)):
            detail = other.get("/api/offers/%d/" % self.offer.pk).json()
            self.assertFalse(detail["mine"])
            self.assertNotIn("applications_count", detail)
        response = client.delete("/api/offers/%d/" % self.offer.pk)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"non_field_errors": ["This offer has received applications: close it instead of deleting it."]},
        )
        self.assertEqual(client.delete("/api/offers/%d/" % empty.pk).status_code, 204)
        # Closed, the applications stay and the employer still reads them
        self.assertEqual(self.post(client, "/api/offers/%d/close/" % self.offer.pk).status_code, 200)
        self.assertEqual(len(client.get("/api/applications/?offer=%d" % self.offer.pk).json()), 2)

    # ── The news ──────────────────────────────────────────────────────

    def unseen(self, client):
        return client.get("/api/applications/unseen/").json()["count"]

    def test_a_new_application_is_news_for_the_employer_once(self):
        employer, candidate = self.login(self.employer), self.login(self.candidate)
        self.assertEqual(self.apply(candidate).status_code, 201)
        self.application(candidate=self.other_candidate)
        # Not for the candidate who sent it, nor for another employer
        self.assertEqual(self.unseen(candidate), 0)
        self.assertEqual(self.unseen(self.login(self.other_employer)), 0)
        self.assertEqual(self.unseen(employer), 2)
        # The list flags them once, then they are seen
        self.assertEqual([a["unseen"] for a in employer.get("/api/applications/").json()], [True, True])
        self.assertEqual(self.unseen(employer), 0)
        self.assertEqual([a["unseen"] for a in employer.get("/api/applications/").json()], [False, False])

    def test_a_move_is_news_for_the_candidate_once(self):
        application = self.application()
        employer, candidate = self.login(self.employer), self.login(self.candidate)
        employer.get("/api/applications/")
        self.post(employer, "/api/applications/%d/status/" % application.pk, {"status": "in_progress"})
        self.post(employer, "/api/applications/%d/status/" % application.pk, {"status": "accepted"})
        # Two moves of one application: one application with news
        self.assertEqual(self.unseen(candidate), 1)
        # The employer's own moves are no news to them
        self.assertEqual(self.unseen(employer), 0)
        self.assertTrue(candidate.get("/api/applications/").json()[0]["unseen"])
        self.assertEqual(self.unseen(candidate), 0)

    def test_a_filtered_list_marks_only_what_it_shows(self):
        employer = self.login(self.employer)
        self.application()
        other_offer = JobOffer.objects.create(
            employer=self.company, status="published", **{**OFFER, "title": "Vue developer"}
        )
        self.application(offer=other_offer)
        employer.get("/api/applications/?offer=%d" % self.offer.pk)
        self.assertEqual(self.unseen(employer), 1)
        # A visitor has no news, only a refusal
        self.assertEqual(Client().get("/api/applications/unseen/").status_code, 403)
