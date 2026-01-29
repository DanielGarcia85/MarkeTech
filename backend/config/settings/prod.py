from .base import *  # noqa

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "postgres"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

def _csv_env(name: str, default: str = "") -> list[str]:
    """
    Read a comma-separated env var and return a clean list.
    Example: "a, b ,c" -> ["a", "b", "c"]
    """
    raw = os.getenv(name, default)
    return [v.strip() for v in raw.split(",") if v.strip()]

# --- Django hosts (no scheme) ---
ALLOWED_HOSTS = _csv_env("DJANGO_ALLOWED_HOSTS", "localhost")

# --- CSRF trusted origins (full origins with scheme) ---
CSRF_TRUSTED_ORIGINS = _csv_env("DJANGO_CSRF_TRUSTED_ORIGINS", "http://localhost")

# --- CORS allowed origins (full origins with scheme) ---
# Only useful if install/configure django-cors-headers.
CORS_ALLOWED_ORIGINS = _csv_env("DJANGO_CORS_ALLOWED_ORIGINS", "")


