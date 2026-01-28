#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "[entrypoint] Starting Django container..."

# Apply database migrations
echo "[entrypoint] Apply database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "[entrypoint] Collect static files..."
python manage.py collectstatic --noinput

# Create superuser only if it doesn't exist
echo "[entrypoint] Ensure superuser exists..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created:', username)
else:
    print('Superuser already exists:', username)
"

# Start Gunicorn server
echo "[entrypoint] Starting Gunicorn"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
