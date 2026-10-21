# backend/messaging/models.py

"""
Message model — what a candidate and an employer write about an application
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Define a message: the application it is about, who wrote it, its text,
when it was sent and when the other participant read it. There is no
conversation table: the conversation of an application is the list of its
messages (application.messages), so that it exists from its first message
on, and has no state of its own (decisions of 21.10.2026).

The rules of the conversation follow the state of the application, and
live in the API, not here: it opens when the employer moves the
application in progress, stays open while it is in progress, is read only
once the application is accepted or rejected, and opens again if the
employer moves it back in progress. Only the candidate and the employer of
the offer take part. The messages go with the application (withdrawn by
the candidate, or deleted with an account or an offer).

What is not here
────────────────
Who may read or write (the views), the number of unread messages (counted
by the API from read_at), the pages.
"""

from django.conf import settings
from django.db import models

from applications.models import JobApplication

# The longest message accepted: a few paragraphs, not a document
MAX_LENGTH = 2000


class Message(models.Model):
    """One message of the conversation of an application."""

    # Deleted with the application; from the application:
    # application.messages
    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    # The candidate or the employer of the offer. An account deleted takes
    # its applications or its offers with it, and so the messages already
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    body = models.TextField(max_length=MAX_LENGTH)
    sent_at = models.DateTimeField(auto_now_add=True)
    # Set when the other participant opens the conversation; empty until then
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Oldest first: a conversation reads from top to bottom
        ordering = ["sent_at", "pk"]
        constraints = [
            # A message says something, refused by the database itself
            models.CheckConstraint(
                condition=~models.Q(body=""),
                name="message_body_not_empty",
                violation_error_message="A message cannot be empty.",
            ),
        ]

    def __str__(self):
        return f"Message {self.pk} on application {self.application_id}"
