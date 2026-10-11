# backend/config/asgi.py

"""
ASGI entry point — exposes the application to an asynchronous server
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Build the ASGI application object that a server calls for each request. An
ASGI server can keep a connection open, which WebSockets require. The
synchronous counterpart is wsgi.py.

Settings
────────
The settings module is not chosen here. DJANGO_SETTINGS_MODULE must be set in
the environment, otherwise the application refuses to start.

References
──────────
  - https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

from django.core.asgi import get_asgi_application

# Object called by the server, referenced as "config.asgi:application"
application = get_asgi_application()
