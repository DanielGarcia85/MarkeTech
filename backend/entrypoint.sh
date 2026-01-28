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

# Create superuser
echo "[entrypoint] Creating superuser..."
python manage.py createsuperuser --noinput

# Start Gunicorn server
echo "[entrypoint] Starting Gunicorn"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
