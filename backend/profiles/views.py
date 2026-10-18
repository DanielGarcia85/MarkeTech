# backend/profiles/views.py

"""
Profile views — the API of the profiles and of the files
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Answer the requests of the frontend about the profile of the logged-in user
(read it, change it, remove one of its files, add or remove a document), and
serve the files of the users after checking who asks. Decides who may do
what; the shape of the data is in serializers.py, the rules of the files in
validators.py.

Routes (profiles/urls.py, under /api/)
──────────────────────────────────────
  GET, PATCH  profile/                  the profile of the user, by role
  DELETE      profile/photo/, cv/       candidate: remove that file
  DELETE      profile/logo/             employer: remove the logo
  POST        profile/documents/        candidate: add a document
  DELETE      profile/documents/<id>/   candidate: remove one of theirs
  GET         files/<path>              a file, when the user may read it

Who may do what
───────────────
Every route needs a logged-in user (the default of the project), except the
files: a logo is public, so the check is made on the path instead. A user
without a role (an administrator) has no profile: 404. Anything a user may
not see answers 404, never 403: the API does not say what exists.
"""

import os

from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User

from .models import CandidateProfile, EmployerProfile
from .serializers import (
    CandidateDocumentSerializer,
    CandidateProfileSerializer,
    EmployerProfileSerializer,
)

# How many further documents a candidate may keep (decision of 18.10.2026)
MAX_DOCUMENTS = 10

# What each role has: its model, its serializer, the names of its file fields
ROLES = {
    User.Role.CANDIDATE: (CandidateProfile, CandidateProfileSerializer, ("photo", "cv")),
    User.Role.EMPLOYER: (EmployerProfile, EmployerProfileSerializer, ("logo",)),
}


def profile_of(user):
    """The profile of the user with its serializer class and its file
    fields; created empty when missing (an account made in the admin site).
    404 for a user without a role."""
    if user.role not in ROLES:
        raise Http404
    model, serializer_class, file_fields = ROLES[user.role]
    profile, _ = model.objects.get_or_create(user=user)
    return profile, serializer_class, file_fields


def candidate_profile_of(user):
    """The profile of a candidate; 404 for anyone else."""
    if user.role != User.Role.CANDIDATE:
        raise Http404
    profile, _ = CandidateProfile.objects.get_or_create(user=user)
    return profile


# ── The profile ───────────────────────────────────────────────────────


class ProfileView(APIView):
    """The profile of the logged-in user: read it, change part of it."""

    def get(self, request):
        profile, serializer_class, _ = profile_of(request.user)
        return Response(serializer_class(profile).data)

    def patch(self, request):
        # partial: only the fields sent change, the others keep their value.
        # The data may be JSON (text fields) or multipart (with files)
        profile, serializer_class, _ = profile_of(request.user)
        serializer = serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfileFileView(APIView):
    """One file of the profile, named by the route: remove it."""

    def delete(self, request, field):
        profile, serializer_class, file_fields = profile_of(request.user)
        if field not in file_fields:
            # The file of the other role: this user has no such thing
            raise Http404
        file = getattr(profile, field)
        if file:
            # Removed from the disk, and the column emptied and saved
            file.delete(save=True)
        return Response(serializer_class(profile).data)


# ── The documents of a candidate ──────────────────────────────────────


class DocumentListView(APIView):
    """Further documents of a candidate: add one."""

    def post(self, request):
        profile = candidate_profile_of(request.user)
        if profile.documents.count() >= MAX_DOCUMENTS:
            raise ValidationError(
                {"file": [f"At most {MAX_DOCUMENTS} documents can be kept."]},
                code="too_many_documents",
            )
        serializer = CandidateDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # The owner is the logged-in user, never a value sent by the client
        serializer.save(candidate=profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentView(APIView):
    """One document of the candidate: remove it."""

    def delete(self, request, pk):
        profile = candidate_profile_of(request.user)
        # Searched among the documents of this profile only: a document of
        # someone else is a 404
        document = get_object_or_404(profile.documents, pk=pk)
        # The file leaves the disk with the record (signals.py)
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── The files ─────────────────────────────────────────────────────────


class FileView(APIView):
    """A file of a user, served once the path says the user may read it."""

    # Logos are public: no login required here, the check is on the path
    permission_classes = [AllowAny]

    def get(self, request, path):
        if not self.may_read(request.user, path) or not default_storage.exists(path):
            raise Http404
        # Streamed from the disk, with its type guessed from its name, and
        # its name for the browser (inline: an image or a PDF is displayed,
        # a .docx is downloaded)
        return FileResponse(
            default_storage.open(path, "rb"),
            filename=os.path.basename(path),
        )

    @staticmethod
    def may_read(user, path):
        """employers/<id>/...: anyone. candidates/<id>/...: that account, or
        an administrator. Anything else, including a path that climbs out of
        its folder: no."""
        parts = path.split("/")
        if len(parts) < 3 or "" in parts or ".." in parts or not parts[1].isdigit():
            return False
        folder, owner = parts[0], int(parts[1])
        if folder == "employers":
            return True
        if folder == "candidates":
            return user.is_authenticated and (user.is_staff or user.pk == owner)
        return False
