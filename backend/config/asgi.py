# backend/config/asgi.py

"""
ASGI entry point — exposes the application to an asynchronous server
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Build the ASGI application object that a server calls for each request. An
ASGI server can keep a connection open, which WebSockets require. The
synchronous counterpart is wsgi.py.

References
──────────
  - https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Use the project settings unless the environment already names a module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Object called by the server, referenced as "config.asgi:application"
application = get_asgi_application()
