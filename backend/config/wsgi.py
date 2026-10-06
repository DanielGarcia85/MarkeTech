# backend/config/wsgi.py

"""
WSGI entry point — exposes the application to a synchronous server
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Build the WSGI application object that a server calls for each request. Used
by the development server (runserver). The asynchronous counterpart is
asgi.py.

References
──────────
  - https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use the project settings unless the environment already names a module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Object called by the server, referenced as "config.wsgi:application"
application = get_wsgi_application()
