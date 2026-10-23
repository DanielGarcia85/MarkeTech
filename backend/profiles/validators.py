# backend/profiles/validators.py

"""
Profile validators — rules applied to the files the users send
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Refuse a file that is too big, or of a type the site does not accept,
wherever the file comes from: the API, the admin site or a test. Django
runs these checks each time a form or a serializer validates a model field.

Why in the model layer
──────────────────────
A check written in one view protects that view only. Attached to the fields
of the models, the same rules hold for every path that writes a file.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.validators import FileExtensionValidator

# Largest file accepted, in bytes: 5 MB (decision of 18.10.2026)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Extensions accepted, by kind of file. Django compares them in lower case
# and without the dot
IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]
DOCUMENT_EXTENSIONS = ["pdf", "docx"]
ATTACHMENT_EXTENSIONS = DOCUMENT_EXTENSIONS + IMAGE_EXTENSIONS


def validate_file_size(file):
    """Refuse a file bigger than MAX_FILE_SIZE."""
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            _("The file is too big (%(size).1f MB); the limit is %(limit)d MB."),
            code="file_too_big",
            params={
                "size": file.size / (1024 * 1024),
                "limit": MAX_FILE_SIZE // (1024 * 1024),
            },
        )


# One validator per kind of file, shared by the model fields
validate_image_extension = FileExtensionValidator(IMAGE_EXTENSIONS)
validate_document_extension = FileExtensionValidator(DOCUMENT_EXTENSIONS)
validate_attachment_extension = FileExtensionValidator(ATTACHMENT_EXTENSIONS)
