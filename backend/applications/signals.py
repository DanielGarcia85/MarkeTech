# backend/applications/signals.py

"""
Application signals — files removed from the disk with their record
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Delete the files of an application or of an attachment when that record is
deleted. Django removes the row and keeps the file: without this, a
withdrawn application, a deleted offer or a deleted account would leave its
CV and letter under MEDIA_ROOT.

Why a signal
────────────
A deletion can start anywhere: the API, the admin site, or the cascade that
follows the deletion of the offer or of the account. The cascade does not
call the delete() method of the application, so a signal, sent by Django
after every deletion, is the only hook that catches them all; the cascade
sends it for each attachment too. The module is imported by apps.py, which
is what registers the receivers below.
"""

from django.db.models.signals import post_delete
from django.dispatch import receiver

from profiles.signals import remove_files

from .models import Attachment, JobApplication


@receiver(post_delete, sender=JobApplication)
def application_deleted(sender, instance, **kwargs):
    """An application is gone: so are its CV and its letter."""
    remove_files(instance, "cv", "cover_letter")


@receiver(post_delete, sender=Attachment)
def attachment_deleted(sender, instance, **kwargs):
    """An attachment record is gone: so is its file."""
    remove_files(instance, "file")
