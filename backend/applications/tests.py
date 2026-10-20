# backend/applications/tests.py

"""
Application tests — the job applications
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Check the models of the applications: the history is written by the model
at the creation and at each change of status, a candidate applies once per
offer, the files land in the folder of the application and leave the disk
with it, whether the application is deleted itself or with its offer.
"""

import os
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings

from accounts.models import User
from offers.models import JobOffer
from profiles.models import CandidateProfile, EmployerProfile

from .models import Attachment, JobApplication

PASSWORD = "Correct-horse-9"
PDF = b"%PDF-1.4 fake"

# Files land here during the tests, never in the media folder of the project
MEDIA = tempfile.mkdtemp(prefix="marketech-tests-")


def pdf(name):
    """A file as the API receives it, with a PDF content."""
    return SimpleUploadedFile(name, PDF)


@override_settings(MEDIA_ROOT=MEDIA)
class ApplicationModelTests(TestCase):
    """The application, its history, its uniqueness and its files."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        # The files of the previous test: a name already taken would get a
        # suffix, and the paths below are checked in full
        shutil.rmtree(MEDIA, ignore_errors=True)
        candidate = User.objects.create_user(
            email="cand@example.com", password=PASSWORD, role="candidate"
        )
        employer = User.objects.create_user(
            email="emp@example.com", password=PASSWORD, role="employer"
        )
        self.candidate = CandidateProfile.objects.create(user=candidate)
        company = EmployerProfile.objects.create(user=employer, company_name="Acme")
        self.offer = JobOffer.objects.create(
            employer=company,
            title="Python developer",
            description="Django and Vue.",
            city="Geneva",
            country="CH",
            contract="permanent",
            status="published",
        )

    def apply(self, **fields):
        """A new application of the candidate to the offer, with a CV."""
        fields.setdefault("cv", pdf("cv.pdf"))
        return JobApplication.objects.create(offer=self.offer, candidate=self.candidate, **fields)

    @staticmethod
    def exists(name):
        """Whether the file of that name is on the disk."""
        return os.path.exists(os.path.join(MEDIA, name))

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
        self.assertTrue(self.exists(application.cv.name))
        self.assertTrue(self.exists(attachment.file.name))

    def test_the_files_go_with_the_application(self):
        application = self.apply(cover_letter=pdf("letter.pdf"))
        attachment = Attachment.objects.create(application=application, file=pdf("diploma.pdf"))
        # The names, before the deletion empties the fields
        names = [application.cv.name, application.cover_letter.name, attachment.file.name]
        self.assertTrue(all(self.exists(name) for name in names))
        application.delete()
        self.assertFalse(any(self.exists(name) for name in names))
        self.assertEqual(Attachment.objects.count(), 0)

    def test_the_files_go_with_the_offer(self):
        application = self.apply()
        attachment = Attachment.objects.create(application=application, file=pdf("diploma.pdf"))
        names = [application.cv.name, attachment.file.name]
        # The cascade of the offer: no delete() called on the application
        self.offer.delete()
        self.assertEqual(JobApplication.objects.count(), 0)
        self.assertFalse(any(self.exists(name) for name in names))
