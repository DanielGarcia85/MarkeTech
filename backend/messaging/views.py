# backend/messaging/views.py

"""
Messaging views — the API of the conversations
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Answer the requests about the conversations: the conversation of an
application, read and written by its two participants; the list of one's
conversations, open or closed; the number of unread messages, for the side
bar. Decides who may read or write; the shape of the data is in
serializers.py. The message that comes with a move of the state is written
by the applications API (applications/views.py, change_status).

Routes (messaging/urls.py, under /api/)
───────────────────────────────────────
  GET   applications/<id>/messages/   the conversation: its head and its
                                      messages, oldest first; the other's
                                      messages become read
  POST  applications/<id>/messages/   write {body}, while the application is
                                      in progress
  GET   messages/                     my conversations, newest activity
                                      first (?state=open or ?state=closed)
  GET   messages/unread/              my unread messages: {count, open, closed}

Who may do what
───────────────
A logged-in user, else 403. Then only the two participants of an
application reach its conversation, the candidate who sent it and the
employer of the offer: anyone else gets 404, never 403 (the API does not
say what exists). Writing needs the application in progress; before (not
taken up) and after (decided), 400.
"""

from django.db.models import Count, Exists, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.models import JobApplication

from .models import Message
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    WriteSerializer,
    head,
    is_open,
)


def mine(user):
    """The applications of which the user is a participant: those they
    sent as a candidate, those to their offers as an employer."""
    return Q(candidate__user=user) | Q(offer__employer__user=user)


def unread_by(user):
    """The messages the user has not read: written by the other
    participant, never opened."""
    return Q(read_at__isnull=True) & ~Q(author=user)


class ConversationView(APIView):
    """The conversation of one application."""

    permission_classes = [permissions.IsAuthenticated]

    def application(self, request, pk):
        """The application, if the user takes part in it; 404 otherwise."""
        applications = JobApplication.objects.filter(mine(request.user)).select_related(
            "offer__employer", "candidate__user"
        )
        return get_object_or_404(applications, pk=pk)

    def get(self, request, pk):
        """The head and the messages; reading marks the other's messages
        read, in one UPDATE, before they are sent back."""
        application = self.application(request, pk)
        application.messages.filter(unread_by(request.user)).update(read_at=timezone.now())
        data = head(application, request.user)
        context = {"request": request}
        messages = MessageSerializer(application.messages.all(), many=True, context=context)
        data["messages"] = messages.data
        return Response(data)

    def post(self, request, pk):
        """A new message, while the application is in progress."""
        application = self.application(request, pk)
        if not is_open(application):
            message = "You can write only while the application is in progress."
            raise ValidationError({"non_field_errors": [message]})
        form = WriteSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        written = Message.objects.create(
            application=application, author=request.user, body=form.validated_data["body"]
        )
        data = MessageSerializer(written, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)


class ConversationListView(APIView):
    """The conversations of the user: one per application that has
    messages, the most recent activity first."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        last = Message.objects.filter(application=OuterRef("pk")).order_by("-sent_at", "-pk")
        applications = (
            JobApplication.objects.filter(mine(user))
            # A conversation exists from its first message on
            .filter(Exists(Message.objects.filter(application=OuterRef("pk"))))
            .annotate(
                last_body=Subquery(last.values("body")[:1]),
                last_author=Subquery(last.values("author")[:1]),
                last_sent_at=Subquery(last.values("sent_at")[:1]),
                unread=Count(
                    "messages",
                    filter=Q(messages__read_at__isnull=True) & ~Q(messages__author=user),
                ),
            )
            .select_related("offer__employer", "candidate__user")
            .order_by("-last_sent_at")
        )
        state = request.query_params.get("state", "")
        if state == "open":
            applications = applications.filter(status=JobApplication.Status.IN_PROGRESS)
        elif state == "closed":
            applications = applications.exclude(status=JobApplication.Status.IN_PROGRESS)
        data = ConversationSerializer(applications, many=True, context={"request": request}).data
        return Response(data)


class UnreadView(APIView):
    """How many messages the user has not read, in all and by state of the
    conversation: the side bar shows them next to its two links. A
    conversation closed by a decision may hold one unread message, the
    last one."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        in_progress = Q(application__status=JobApplication.Status.IN_PROGRESS)
        counts = Message.objects.filter(
            unread_by(user), application__in=JobApplication.objects.filter(mine(user))
        ).aggregate(
            count=Count("pk"),
            open=Count("pk", filter=in_progress),
            closed=Count("pk", filter=~in_progress),
        )
        return Response(counts)
