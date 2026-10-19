# backend/profiles/signals.py

"""
Profile signals — files removed from the disk with their record
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Delete the files of a profile or of a document when that record is deleted.
Django removes the row and keeps the file: without this, a deleted account
would leave its CV and photo under MEDIA_ROOT.

Why a signal
────────────
A deletion can start anywhere: the admin site, the API, or the cascade that
follows the deletion of the account. The cascade does not call the delete()
method of the profile, so a signal, sent by Django after every deletion, is
the only hook that catches them all. The module is imported by apps.py,
which is what registers the receivers below.
"""

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import CandidateDocument, CandidateProfile, EmployerProfile


def remove_files(instance, *field_names):
    """Delete from the storage the files of the given fields, when set."""
    for name in field_names:
        field_file = getattr(instance, name)
        if field_file:
            # save=False: the record is already gone, nothing to update
            field_file.delete(save=False)


@receiver(post_delete, sender=CandidateProfile)
def candidate_profile_deleted(sender, instance, **kwargs):
    """A candidate profile is gone: so are the photo and the CV."""
    remove_files(instance, "photo", "cv")


@receiver(post_delete, sender=CandidateDocument)
def candidate_document_deleted(sender, instance, **kwargs):
    """A document record is gone: so is its file."""
    remove_files(instance, "file")


@receiver(post_delete, sender=EmployerProfile)
def employer_profile_deleted(sender, instance, **kwargs):
    """An employer profile is gone: so are the photo and the logo."""
    remove_files(instance, "photo", "logo")
