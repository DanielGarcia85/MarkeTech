# backend/config/asgi.py

"""
ASGI entry point — exposes the application to an asynchronous server
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Build the ASGI application object that the server (Daphne) calls for each
connection, and send each one where it belongs (decisions of 26.10.2026):
an HTTP request to Django, as before; a WebSocket to the consumer of the
live application (live/routing.py). An ASGI server can keep a connection
open, which WebSockets require. The synchronous counterpart is wsgi.py.

The WebSockets
──────────────
Before the consumer, two checks, from the outside in:
- the origin: the page that opens the connection must come from one of
  the ALLOWED_HOSTS; a WebSocket has no CSRF token, and a browser sends
  the session cookie to it from any site;
- the user: read from the session cookie, as for the API, and put in the
  scope of the connection, where the consumer reads it.

Settings
────────
The settings module is not chosen here. DJANGO_SETTINGS_MODULE must be set in
the environment, otherwise the application refuses to start.

References
──────────
  - https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
  - https://channels.readthedocs.io/en/stable/deploying.html
"""

from django.core.asgi import get_asgi_application

# Django is started first: what is imported below reads the models and the
# settings, which must be ready
django_application = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from live.routing import websocket_urlpatterns

# Object called by the server, referenced as "config.asgi:application"
application = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
