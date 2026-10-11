# backend/config/wsgi.py

"""
WSGI entry point — exposes the application to a synchronous server
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Build the WSGI application object that a server calls for each request. Used
by the development server (runserver). The asynchronous counterpart is
asgi.py.

Settings
────────
The settings module is not chosen here. DJANGO_SETTINGS_MODULE must be set in
the environment, otherwise the application refuses to start.

References
──────────
  - https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

# Object called by the server, referenced as "config.wsgi:application"
application = get_wsgi_application()
