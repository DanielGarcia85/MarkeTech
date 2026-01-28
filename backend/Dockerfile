# backend/Dockerfile

# Python base image (Debian slim): lightweight and suitable for production
FROM python:3.13-slim

## Set environment variables
# Prevents Python from writing .pyc files (cleaner images)
ENV PYTHONDONTWRITEBYTECODE=1
# Forces logs to be output immediately (useful for Docker logs)
ENV PYTHONUNBUFFERED=1

# Set working directory in the container
WORKDIR /app

# Install the minimum system dependencies (curl is used for HEALTHCHECK)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    # Then clean the apt cache to reduce the image size
    && rm -rf /var/lib/apt/lists/*

# Copy the Python dependencies file first (better Docker cache)
COPY requirements.txt /app/requirements.txt

# Update pip
RUN pip install --upgrade pip \
    # Install Python dependencies
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy project files (all the backend code into the image)
COPY . /app

# Ensure scripts are executable (required on Linux)
RUN chmod +x /app/entrypoint.sh

# Create a non-root user (good security practice in production)
# Prepare the folders used by collectstatic and media
# Give permissions to the non-root user
RUN addgroup --system app \
    && adduser --system --group app \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R app:app /app

# Switch execution to non-root user
USER app

# Exposes the container's application port
EXPOSE 8000

#(Optionnel) Healthcheck to verify that the API is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/api/health/ || exit 1

# Launch the backend via the input script (migrate + collectstatic + gunicorn)
CMD ["/app/entrypoint.sh"]
