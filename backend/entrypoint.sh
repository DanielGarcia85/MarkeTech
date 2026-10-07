#!/bin/sh
# backend/entrypoint.sh
#
# Container start-up — prepares the application, then starts the server
# ─────────────────────────────────────────────────────────────────────────────
# Runs every time the backend container starts.

# Stop at the first command that fails: never start the server on a
# half-prepared application
set -e

# Bring the database schema up to date
echo "[entrypoint] Applying database migrations"
python manage.py migrate --noinput

# Gather the static files where Whitenoise serves them from
echo "[entrypoint] Collecting static files"
python manage.py collectstatic --noinput

# Create the administrator account on the first start. The three values come
# from the environment and have no default: if one is missing, no account is
# created.
echo "[entrypoint] Checking the administrator account"
python manage.py shell --no-imports -c "
import os
from django.contrib.auth import get_user_model

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

User = get_user_model()
if not (username and email and password):
    print('Administrator variables not all set: no account created')
elif User.objects.filter(username=username).exists():
    print('Administrator already exists:', username)
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Administrator created:', username)
"

# Replace this script by the server, so that it receives the stop signals
# sent by Docker and shuts down cleanly
echo "[entrypoint] Starting Daphne"
exec daphne -b 0.0.0.0 -p 8000 config.asgi:application
