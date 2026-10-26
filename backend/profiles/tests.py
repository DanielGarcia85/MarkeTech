# backend/profiles/tests.py

"""
Profile tests — the profiles API and the files of the users
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the profiles API as the frontend will use it: a logged-in user reads
and changes their profile, sends and removes files, adds and removes
documents; the files are served to the right people only; the rules of
size and type hold; nothing stays on the disk after a removal. The files
go to a temporary folder, deleted at the end.
"""

import io
import json
import os
import shutil
import tempfile

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from PIL import Image

from accounts.models import User

from .models import CandidateDocument, CandidateProfile, EmployerProfile
from .validators import MAX_FILE_SIZE
from .views import MAX_DOCUMENTS

PASSWORD = "Correct-horse-9"
PDF = b"%PDF-1.4 fake"

# Files land here during the tests, never in the media folder of the project
MEDIA = tempfile.mkdtemp(prefix="marketech-tests-")


def png():
    """A real 4 by 4 image, as bytes: Pillow checks the content."""
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), "white").save(buffer, "PNG")
    return buffer.getvalue()


@override_settings(MEDIA_ROOT=MEDIA)
class ProfileApiTests(TestCase):
    """The profile of the logged-in user, its files and its documents."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.candidate = User.objects.create_user(
            email="cand@example.com", password=PASSWORD, role="candidate"
        )
        self.employer = User.objects.create_user(
            email="emp@example.com", password=PASSWORD, role="employer"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password=PASSWORD
        )

    # ── Helpers ───────────────────────────────────────────────────────

    def login(self, user):
        """A client logged in as the user, with the CSRF token a browser
        would send back (enforced, as in the account tests)."""
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        # The session route of allauth sets the CSRF cookie
        client.get("/_allauth/browser/v1/auth/session")
        client.defaults["HTTP_X_CSRFTOKEN"] = client.cookies["csrftoken"].value
        return client

    def patch_json(self, client, data):
        return client.patch(
            "/api/profile/", data=json.dumps(data), content_type="application/json"
        )

    def patch_files(self, client, files):
        return client.patch(
            "/api/profile/",
            data=encode_multipart(BOUNDARY, files),
            content_type=MULTIPART_CONTENT,
        )

    def file(self, name, content):
        """An uploaded file for the test client: a name and a content."""
        return SimpleUploadedFile(name, content)

    def on_disk(self, url):
        """Whether the file behind a URL of the API exists in MEDIA_ROOT."""
        return os.path.exists(os.path.join(MEDIA, url.removeprefix("/api/files/")))

    def status(self, client, url):
        """Status of a GET on a file URL, the file closed at once. A served
        file stays open until its response is closed, and Windows refuses
        to delete an open file: a test that removes the file next would
        fail there, and only there. Read to its end, the file is closed by
        the test client itself. Never response.close(): it sends the signal
        of a finished request, which closes the database connection of the
        test; SQLite in memory ignores it, PostgreSQL refuses every query
        after it (found on 22.10.2026)."""
        response = client.get(url)
        if response.streaming:
            b"".join(response.streaming_content)
        return response.status_code

    # ── The profile ───────────────────────────────────────────────────

    def test_signup_creates_the_profile_of_the_role(self):
        client = Client(enforce_csrf_checks=True)
        client.get("/_allauth/browser/v1/auth/session")
        for role, model in (("candidate", CandidateProfile), ("employer", EmployerProfile)):
            client.post(
                "/_allauth/browser/v1/auth/signup",
                data=json.dumps({
                    "email": f"new-{role}@example.com",
                    "password": PASSWORD,
                    "first_name": "Léa",
                    "last_name": "Doe",
                    "role": role,
                    "terms": True,
                }),
                content_type="application/json",
                HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
            )
            user = User.objects.get(email=f"new-{role}@example.com")
            self.assertTrue(model.objects.filter(user=user).exists())
        self.assertEqual(CandidateProfile.objects.count(), 1)
        self.assertEqual(EmployerProfile.objects.count(), 1)

    def test_the_profile_needs_a_login_and_a_role(self):
        self.assertEqual(Client().get("/api/profile/").status_code, 403)
        # An administrator has no role, hence no profile
        self.assertEqual(self.login(self.admin).get("/api/profile/").status_code, 404)

    def test_a_missing_profile_is_created_on_first_read(self):
        # An account made in the admin site has a role but no profile yet
        self.assertFalse(CandidateProfile.objects.filter(user=self.candidate).exists())
        response = self.login(self.candidate).get("/api/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["city"], "")
        self.assertEqual(response.json()["documents"], [])
        self.assertTrue(CandidateProfile.objects.filter(user=self.candidate).exists())

    def test_the_names_of_the_account_are_changed_with_the_profile(self):
        client = self.login(self.candidate)
        response = self.patch_json(client, {"first_name": "Léa", "last_name": "Doe"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["first_name"], "Léa")
        self.candidate.refresh_from_db()
        self.assertEqual((self.candidate.first_name, self.candidate.last_name), ("Léa", "Doe"))
        # Never blank, and the address is read only here
        self.assertEqual(self.patch_json(client, {"last_name": ""}).status_code, 400)
        response = self.patch_json(client, {"email": "other@example.com"})
        self.assertEqual(response.json()["email"], "cand@example.com")

    def test_the_language_and_the_notifications_change_with_the_profile(self):
        client = self.login(self.candidate)
        data = client.get("/api/profile/").json()
        self.assertEqual((data["language"], data["notify_by_email"]), ("", True))
        response = self.patch_json(client, {"language": "fr", "notify_by_email": False})
        self.assertEqual(response.status_code, 200)
        self.candidate.refresh_from_db()
        self.assertEqual((self.candidate.language, self.candidate.notify_by_email), ("fr", False))
        # Only a language the site offers
        response = self.patch_json(client, {"language": "de"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("language", response.json())

    def test_patch_changes_the_fields_sent_only(self):
        client = self.login(self.employer)
        self.patch_json(client, {"company_name": "Acme SA", "city": "Geneva"})
        response = self.patch_json(client, {"country": "CH"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            (data["company_name"], data["city"], data["country"]),
            ("Acme SA", "Geneva", "CH"),
        )
        # Read-only and unknown fields are ignored, not refused
        response = self.patch_json(client, {"updated_at": "2000-01-01", "role": "admin"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["updated_at"].startswith("20"))

    def test_a_country_is_a_code_of_the_list(self):
        client = self.login(self.employer)
        response = self.patch_json(client, {"country": "FR", "company_country": "CH"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual((response.json()["country"], response.json()["company_country"]), ("FR", "CH"))
        # A name of the list is accepted and stored as its code; anything
        # else is refused, field by field
        response = self.patch_json(client, {"country": "Switzerland"})
        self.assertEqual((response.status_code, response.json()["country"]), (200, "CH"))
        response = self.patch_json(client, {"country": "Nowhere"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("country", response.json())
        self.assertEqual(self.patch_json(client, {"company_country": "XX"}).status_code, 400)
        # Empty means none
        response = self.patch_json(client, {"country": ""})
        self.assertEqual((response.status_code, response.json()["country"]), (200, ""))

    def test_the_countries_are_listed_in_the_language_of_the_request(self):
        # Public: a visitor gets the list too
        response = Client().get("/api/countries/", HTTP_ACCEPT_LANGUAGE="fr-CH")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Switzerland and France first, then the alphabet, the two repeated
        self.assertEqual(data[:2], [{"code": "CH", "name": "Suisse"}, {"code": "FR", "name": "France"}])
        self.assertEqual(data[2], {"code": "AF", "name": "Afghanistan"})
        self.assertEqual(len({item["code"] for item in data}), len(data) - 2)
        self.assertIn({"code": "DE", "name": "Allemagne"}, data)
        response = Client().get("/api/countries/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertIn({"code": "DE", "name": "Germany"}, response.json())

    # ── The files of the profile ──────────────────────────────────────

    def test_files_are_stored_replaced_and_removed(self):
        client = self.login(self.candidate)
        response = self.patch_files(
            client, {"cv": self.file("my cv.pdf", PDF), "photo": self.file("me.png", png())}
        )
        self.assertEqual(response.status_code, 200)
        cv_url = response.json()["cv"]
        self.assertEqual(cv_url, f"/api/files/candidates/{self.candidate.pk}/my_cv.pdf")
        self.assertTrue(self.on_disk(cv_url))

        # A new CV replaces the old one: one file on the disk, not two
        response = self.patch_files(client, {"cv": self.file("better.pdf", PDF)})
        self.assertEqual(response.json()["cv"], f"/api/files/candidates/{self.candidate.pk}/better.pdf")
        self.assertFalse(self.on_disk(cv_url))
        self.assertTrue(self.on_disk(response.json()["cv"]))

        # DELETE empties the field and the disk, and answers the profile
        response = client.delete("/api/profile/cv/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["cv"])
        self.assertTrue(self.on_disk(response.json()["photo"]))
        self.assertFalse(self.on_disk(f"/api/files/candidates/{self.candidate.pk}/better.pdf"))

        # The file of the other role does not exist for this user
        self.assertEqual(client.delete("/api/profile/logo/").status_code, 404)

    def test_the_rules_of_the_files_are_enforced(self):
        client = self.login(self.candidate)
        cases = (
            ("wrong extension", "cv", self.file("cv.exe", PDF)),
            ("too big", "cv", self.file("cv.pdf", b"x" * (MAX_FILE_SIZE + 1))),
            ("fake image", "photo", self.file("me.png", b"not an image")),
        )
        for label, field, upload in cases:
            response = self.patch_files(client, {field: upload})
            self.assertEqual(response.status_code, 400, label)
            # The error is reported under the name of the field
            self.assertIn(field, response.json(), label)
        self.assertIsNone(client.get("/api/profile/").json()["cv"])
        # The reason in the language of the interface
        client.defaults["HTTP_ACCEPT_LANGUAGE"] = "fr"
        response = self.patch_files(client, {"cv": self.file("cv.pdf", b"x" * (MAX_FILE_SIZE + 1))})
        self.assertEqual(
            response.json(), {"cv": ["Le fichier est trop volumineux (5.0 Mo) ; la limite est de 5 Mo."]}
        )

    # ── The documents ─────────────────────────────────────────────────

    def test_documents_are_added_listed_and_removed(self):
        client = self.login(self.candidate)
        response = client.post("/api/profile/documents/", {"file": self.file("cert.pdf", PDF)})
        self.assertEqual(response.status_code, 201)
        document = response.json()
        self.assertEqual(document["name"], "cert.pdf")
        self.assertTrue(self.on_disk(document["file"]))
        self.assertEqual(client.get("/api/profile/").json()["documents"][0]["id"], document["id"])

        # Someone else cannot remove it; an employer has no documents at all
        other = self.login(self.employer)
        self.assertEqual(other.delete(f"/api/profile/documents/{document['id']}/").status_code, 404)
        self.assertEqual(other.post("/api/profile/documents/", {"file": self.file("x.pdf", PDF)}).status_code, 404)

        response = client.delete(f"/api/profile/documents/{document['id']}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(self.on_disk(document["file"]))
        self.assertEqual(client.get("/api/profile/").json()["documents"], [])

    def test_documents_are_limited(self):
        client = self.login(self.candidate)
        for i in range(MAX_DOCUMENTS):
            self.assertEqual(
                client.post("/api/profile/documents/", {"file": self.file(f"d{i}.pdf", PDF)}).status_code,
                201,
            )
        response = client.post("/api/profile/documents/", {"file": self.file("one-more.pdf", PDF)})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"file": ["At most 10 documents can be kept."]})
        response = client.post(
            "/api/profile/documents/",
            {"file": self.file("one-more.pdf", PDF)},
            HTTP_ACCEPT_LANGUAGE="fr",
        )
        self.assertEqual(response.json(), {"file": ["Vous pouvez garder au plus 10 documents."]})
        self.assertEqual(CandidateDocument.objects.count(), MAX_DOCUMENTS)

    # ── The files ─────────────────────────────────────────────────────

    def test_candidate_files_are_private_and_logos_public(self):
        candidate = self.login(self.candidate)
        cv_url = self.patch_files(candidate, {"cv": self.file("cv.pdf", PDF)}).json()["cv"]
        employer = self.login(self.employer)
        logo_url = self.patch_files(employer, {"logo": self.file("logo.png", png())}).json()["logo"]

        response = candidate.get(cv_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertEqual(response["Content-Disposition"], 'inline; filename="cv.pdf"')
        self.assertEqual(b"".join(response.streaming_content), PDF)
        # The owner and an administrator: yes; another user and a visitor: no
        self.assertEqual(self.login(self.admin).get(cv_url).status_code, 200)
        self.assertEqual(employer.get(cv_url).status_code, 404)
        self.assertEqual(Client().get(cv_url).status_code, 404)

        # A logo, in its own public folder: everyone, logged in or not
        self.assertTrue(logo_url.startswith("/api/files/logos/"))
        response = Client().get(logo_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")

    def test_the_photo_of_an_employer_is_private_too(self):
        employer = self.login(self.employer)
        photo_url = self.patch_files(employer, {"photo": self.file("me.png", png())}).json()["photo"]
        self.assertTrue(photo_url.startswith("/api/files/employers/%d/" % self.employer.pk))
        self.assertEqual(self.status(employer, photo_url), 200)
        self.assertEqual(self.status(self.login(self.admin), photo_url), 200)
        self.assertEqual(self.status(self.login(self.candidate), photo_url), 404)
        self.assertEqual(self.status(Client(), photo_url), 404)
        # Removed by its route, like a candidate's; gone from the disk
        response = employer.delete("/api/profile/photo/")
        self.assertEqual((response.status_code, response.json()["photo"]), (200, None))
        self.assertFalse(self.on_disk(photo_url))
        # The whole account: photo and logo leave with it
        photo_url = self.patch_files(employer, {"photo": self.file("me.png", png())}).json()["photo"]
        logo_url = self.patch_files(employer, {"logo": self.file("logo.png", png())}).json()["logo"]
        self.employer.delete()
        self.assertFalse(self.on_disk(photo_url) or self.on_disk(logo_url))

    def test_bad_paths_are_not_found(self):
        client = self.login(self.candidate)
        for path in (
            "candidates/%d/../../settings.py" % self.candidate.pk,
            "candidates/%d/missing.pdf" % self.candidate.pk,
            "candidates/abc/cv.pdf",
            "candidates/%d/" % self.candidate.pk,
            "elsewhere/1/file.pdf",
            "logos/abc/logo.png",
            "cv.pdf",
        ):
            self.assertEqual(client.get("/api/files/" + path).status_code, 404, path)

    # ── The end of an account ─────────────────────────────────────────

    def test_deleting_the_account_removes_the_files(self):
        client = self.login(self.candidate)
        cv_url = self.patch_files(client, {"cv": self.file("cv.pdf", PDF)}).json()["cv"]
        doc_url = client.post("/api/profile/documents/", {"file": self.file("d.pdf", PDF)}).json()["file"]
        self.assertTrue(self.on_disk(cv_url) and self.on_disk(doc_url))
        self.candidate.delete()
        self.assertFalse(self.on_disk(cv_url) or self.on_disk(doc_url))
        self.assertEqual(CandidateProfile.objects.count() + CandidateDocument.objects.count(), 0)
