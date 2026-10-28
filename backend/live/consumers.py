# backend/live/consumers.py

"""
Live consumer — the WebSocket of a logged-in user
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Keep open the WebSocket of each tab where a user is logged in, and pass on
to it the signals the views send (notify.py): something new in the
messages, the applications or the appointments of the user. Channels
creates one object of this class per connection, for as long as it lasts.

Who may connect
───────────────
A logged-in user only, recognised by the session cookie, as by the API
(AuthMiddlewareStack, routing.py). A visitor is refused before the
connection opens; so is a blocked account, which Django no longer counts
as logged in. Demo accounts connect like the others.

What travels
────────────
A signal, never the data (decision of 26.10.2026): {"type": "messages",
"application": 12} says where to look; the page then reads through the
API, which alone decides what the user may see. The browser sends
nothing: whatever arrives from it is ignored.
"""

from channels.generic.websocket import AsyncJsonWebsocketConsumer


def group_of(user_id):
    """The name of the group that gathers every open tab of a user."""
    return f"user_{user_id}"


class LiveConsumer(AsyncJsonWebsocketConsumer):
    """The WebSocket of one tab of a logged-in user."""

    # The group of the user, once the connection is accepted; None while a
    # refused connection is being closed
    group = None

    async def connect(self):
        """Accept a logged-in user and subscribe the tab to their group;
        refuse anybody else (the browser sees the connection fail)."""
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return
        self.group = group_of(user.pk)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        """The tab is closed or the connection lost: leave the group."""
        if self.group:
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def news(self, event):
        """A signal sent to the group by a view (notify.py): passed on to
        the browser as it is, the kind and the application concerned."""
        await self.send_json({"type": event["kind"], "application": event["application"]})
