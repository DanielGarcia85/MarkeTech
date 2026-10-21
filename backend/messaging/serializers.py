# backend/messaging/serializers.py

"""
Messaging serializers — the JSON shape of the conversations
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Turn the messages and the conversations into JSON for the pages: a
message (its text, its dates, whether the user asking wrote it), the head
of a conversation (the application, its offer, the other participant,
whether one may still write), a conversation in the list (the same head,
its last message, how many are unread). Checks what a participant writes.
Who may read or write which conversation is decided by the views.
"""

from rest_framework import serializers

from applications.models import JobApplication

from .models import MAX_LENGTH, Message


def is_open(application):
    """One may write while the application is in progress, and only then
    (decisions of 21.10.2026): before, the employer has not taken it up;
    after, the conversation stays, read only."""
    return application.status == JobApplication.Status.IN_PROGRESS


def head(application, user):
    """What the page of a conversation and the list show of it: the
    application and its state, the offer with its company, the name of the
    other participant (the company for the candidate, the candidate for the
    employer), and whether one may write."""
    offer = application.offer
    company = offer.employer
    if application.candidate.user_id == user.pk:
        other = company.company_name
    else:
        other = application.candidate.user.get_full_name() or application.candidate.user.email
    return {
        "application": application.pk,
        "status": application.status,
        "open": is_open(application),
        "offer": {
            "id": offer.pk,
            "title": offer.title,
            "company": {
                "name": company.company_name,
                "logo": company.logo.url if company.logo else None,
            },
        },
        "other": other,
    }


class MessageSerializer(serializers.ModelSerializer):
    """A message of a conversation; "mine" says whether the user asking
    wrote it (the page puts it on the right)."""

    mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "body", "sent_at", "read_at", "mine"]
        read_only_fields = fields

    def get_mine(self, message):
        return message.author_id == self.context["request"].user.pk


class WriteSerializer(serializers.Serializer):
    """What a participant writes: a text, its spaces around removed, not
    empty, not longer than MAX_LENGTH."""

    body = serializers.CharField(
        max_length=MAX_LENGTH,
        trim_whitespace=True,
        error_messages={
            "blank": "Write a message.",
            "max_length": f"A message has at most {MAX_LENGTH} characters.",
        },
    )


class ConversationSerializer(serializers.Serializer):
    """A conversation in the list: its head, its last message, how many of
    the other's messages are unread. Reads the values annotated by the view
    on the application (last_body, last_author, last_sent_at, unread)."""

    def to_representation(self, application):
        user = self.context["request"].user
        data = head(application, user)
        data["last"] = {
            "body": application.last_body,
            "sent_at": serializers.DateTimeField().to_representation(application.last_sent_at),
            "mine": application.last_author == user.pk,
        }
        data["unread"] = application.unread
        return data

