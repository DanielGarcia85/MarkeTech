# backend/Dockerfile
#
# Backend image — Django application served by Daphne
# ─────────────────────────────────────────────────────────────────────────────
# The same image runs in every environment: what differs between them comes
# from environment variables, never from the image itself.

# Official Python image, "slim" variant: Debian with the bare minimum, and
# the same Python 3.13 as the development workstations
FROM python:3.13-slim

# Do not write .pyc files in the container, and send logs straight to Docker
# instead of keeping them in a buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Folder of the application inside the container
WORKDIR /app

# Dependencies first, on their own: Docker reuses this step from its cache
# as long as requirements.txt does not change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code, except what .dockerignore lists
COPY . .

# Unprivileged user: the application never runs as root. It owns /app
# because the start-up script writes the collected static files there.
RUN useradd --system --user-group --no-create-home app \
    && chmod +x entrypoint.sh \
    && chown -R app:app /app
USER app

# Port Daphne listens on. Declared for documentation: nothing is published
# to the outside from here.
EXPOSE 8000

# Migrations, static files, administrator account, then the server
CMD ["./entrypoint.sh"]
