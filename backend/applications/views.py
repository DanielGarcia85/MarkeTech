# backend/applications/views.py

"""
Application views — the API of the job applications
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Answer the requests about the job applications: a candidate applies to a
published offer, follows their applications and withdraws one; an employer
reads the applications to their offers and moves their state; both read the
files. Decides who may do what and applies the rules of the state; the
shape of the data is in serializers.py.

Routes (applications/urls.py, under /api/, built by the router)
───────────────────────────────────────────────────────────────
  GET     applications/                     mine: candidate, their own;
                                            employer, those to their offers
                                            (?offer=<id>, ?status=<status>)
  GET     applications/<id>/                one of the above
  POST    applications/                     candidate: apply (multipart)
  DELETE  applications/<id>/                candidate: withdraw, before the
                                            employer decided
  POST    applications/<id>/status/         employer: in_progress, accepted
                                            or rejected, with an optional
                                            message for the candidate
  GET     applications/<id>/cv/             the CV, as a file
  GET     applications/<id>/cover-letter/   the letter, as a file
  GET     applications/<id>/attachments/<id>/  one joined document

Who may do what
───────────────
Everything needs a logged-in user: a visitor gets 403. Applying and
withdrawing need a candidate, moving the state needs an employer: the other
role gets 403. Then everyone only ever reaches their own applications, the
candidate those they sent, the employer those to their offers: another
one's answers 404, never 403 (the API does not say what exists). No PATCH:
an application is not edited once sent, its state moves by its own route.

The message of a move
─────────────────────
A move of the state may carry a message from the employer: the first of
the conversation when the application goes in progress, the last one when
it is decided (decisions of 21.10.2026). It is written here, with the
move, in one transaction: the only place where this API knows of the
messaging (messaging/models.py), which otherwise depends on it.
"""

import os

from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from messaging.models import MAX_LENGTH, Message
from offers.views import IsCandidate, IsEmployer, is_candidate, is_employer
from profiles.models import CandidateProfile

from .models import JobApplication
from .serializers import ApplySerializer, JobApplicationSerializer

# ── Who is asking ─────────────────────────────────────────────────────
# The roles and their permissions are those of offers/views.py


def candidate_profile_of(user):
    """The candidate profile of the user, created empty when missing (an
    account made in the admin site), like the profiles API does."""
    profile, _ = CandidateProfile.objects.get_or_create(user=user)
    return profile


# ── The files ─────────────────────────────────────────────────────────


def file_response(field_file):
    """A stored file, streamed from the disk with its type guessed from its
    name and its name for the browser (inline: a PDF is displayed, a .docx
    is downloaded); 404 when the field is empty."""
    if not field_file:
        raise Http404
    return FileResponse(field_file.open("rb"), filename=os.path.basename(field_file.name))


# ── The views ─────────────────────────────────────────────────────────

# What the employer may set; received is the state of a new application only
EMPLOYER_STATUSES = (
    JobApplication.Status.IN_PROGRESS,
    JobApplication.Status.ACCEPTED,
    JobApplication.Status.REJECTED,
)
# Once decided, an application stays: the candidate cannot withdraw it
DECIDED = (JobApplication.Status.ACCEPTED, JobApplication.Status.REJECTED)


class JobApplicationViewSet(viewsets.ModelViewSet):
    """The job applications: sent by the candidates, read by both sides,
    moved by the employers."""

    # No PATCH nor PUT: nothing of an application is edited once sent
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_permissions(self):
        """A candidate to apply and withdraw, an employer to move the state,
        any logged-in user to read."""
        if self.action in ("create", "destroy"):
            return [IsCandidate()]
        if self.action == "change_status":
            return [IsEmployer()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        return ApplySerializer if self.action == "create" else JobApplicationSerializer

    def get_serializer_context(self):
        """The profile of the candidate, for the checks and the copies made
        when applying."""
        context = super().get_serializer_context()
        if self.action == "create":
            context["profile"] = candidate_profile_of(self.request.user)
        return context

    def get_queryset(self):
        """What the request may see: one's own as a candidate, those to
        one's offers as an employer, nothing for anyone else."""
        user = self.request.user
        if is_candidate(user):
            mine = Q(candidate__user=user)
        elif is_employer(user):
            mine = Q(offer__employer__user=user)
        else:
            mine = Q(pk__in=[])
        applications = JobApplication.objects.filter(mine).select_related(
            "offer__employer", "candidate__user"
        )
        if self.action == "list":
            applications = self.filtered(applications)
        return applications

    def filtered(self, applications):
        """The filters of the list, in the query string: ?offer=<id> and
        ?status=<status>; an empty, absent or invalid one does not filter."""
        params = self.request.query_params
        offer = params.get("offer", "")
        if offer.isdigit():
            applications = applications.filter(offer_id=int(offer))
        status_ = params.get("status", "")
        if status_ in JobApplication.Status.values:
            applications = applications.filter(status=status_)
        return applications

    # ── Applying and withdrawing ──────────────────────────────────────

    def create(self, request, *args, **kwargs):
        """Apply: the form is read by ApplySerializer, the answer is the new
        application as the lists show it."""
        form = self.get_serializer(data=request.data)
        form.is_valid(raise_exception=True)
        application = form.save()
        data = JobApplicationSerializer(application, context=self.get_serializer_context()).data
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, application):
        """Withdraw: refused once the employer decided; the files leave the
        disk with the row (signals.py)."""
        if application.status in DECIDED:
            message = "This application has been decided and can no longer be withdrawn."
            raise ValidationError({"non_field_errors": [message]})
        application.delete()

    # ── The state ─────────────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="status")
    def change_status(self, request, pk=None):
        """Employer: in_progress, accepted or rejected, any of them from any
        state but the same; the model records the change in the history.
        An optional message goes to the conversation, written after the
        move (so that a first message finds the application in progress)
        and in the same transaction: both or neither."""
        application = get_object_or_404(self.get_queryset(), pk=pk)
        new_status = request.data.get("status")
        if new_status not in EMPLOYER_STATUSES:
            message = "Choose a status: in_progress, accepted or rejected."
            raise ValidationError({"status": [message]})
        if new_status == application.status:
            message = "The application is already in this status."
            raise ValidationError({"non_field_errors": [message]})
        text = str(request.data.get("message") or "").strip()
        if len(text) > MAX_LENGTH:
            message = f"A message has at most {MAX_LENGTH} characters."
            raise ValidationError({"message": [message]})
        with transaction.atomic():
            application.status = new_status
            application.save()
            if text:
                Message.objects.create(application=application, author=request.user, body=text)
        return Response(self.get_serializer(application).data, status=status.HTTP_200_OK)

    # ── The files ─────────────────────────────────────────────────────

    @action(detail=True, methods=["get"])
    def cv(self, request, pk=None):
        application = get_object_or_404(self.get_queryset(), pk=pk)
        return file_response(application.cv)

    @action(detail=True, methods=["get"], url_path="cover-letter")
    def cover_letter(self, request, pk=None):
        application = get_object_or_404(self.get_queryset(), pk=pk)
        return file_response(application.cover_letter)

    @action(
        detail=True,
        methods=["get"],
        url_path=r"attachments/(?P<attachment_id>\d+)",
        url_name="attachment",
    )
    def attachment(self, request, pk=None, attachment_id=None):
        application = get_object_or_404(self.get_queryset(), pk=pk)
        attachment = get_object_or_404(application.attachments, pk=attachment_id)
        return file_response(attachment.file)
