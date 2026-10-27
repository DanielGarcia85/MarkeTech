# backend/live/routing.py

"""
Live routing — the address of the WebSocket
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Give the WebSocket its address, /ws/, and the consumer that answers it.
The WebSocket counterpart of a urls.py: read by config/asgi.py, which
sends the WebSocket connections here and the HTTP requests to Django.
"""

from django.urls import path

from .consumers import LiveConsumer

# One address for every tab: the consumer knows the user by the session,
# the address does not need to say who
websocket_urlpatterns = [
    path("ws/", LiveConsumer.as_asgi()),
]
