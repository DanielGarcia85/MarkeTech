# backend/messaging/urls.py

"""
Messaging URL table — the routes of the messaging API
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Map the routes of the messaging API to their views, written out one by
one: the conversation hangs under an application, which a router of DRF
does not nest. Included by config/urls.py under the prefix api/, after the
applications. Contains no logic.
"""

from django.urls import path

from .views import ConversationListView, ConversationView, UnreadView

urlpatterns = [
    path("applications/<int:pk>/messages/", ConversationView.as_view(), name="conversation"),
    path("messages/", ConversationListView.as_view(), name="conversation-list"),
    path("messages/unread/", UnreadView.as_view(), name="unread-messages"),
]
