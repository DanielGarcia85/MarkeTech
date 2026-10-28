# backend/config/wsgi.py

"""
WSGI entry point — exposes the application to a synchronous server
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Build the WSGI application object that a synchronous server calls for each
request. Not used to serve the site: Daphne runs asgi.py, in the container
and through runserver. Kept for the tools that expect a WSGI entry point.

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
