#!/usr/bin/env python
# backend/manage.py

"""
Django command line — entry point of every administrative command
─────────────────────────────────────────────────────────────────────────────

Responsibility
──────────────
Select the settings module, then hand the command over to Django (runserver,
migrate, test and so on). Contains no project logic.

Usage
─────
  python manage.py <command> [options]
"""

import os
import sys


def main():
    """Run the Django command given on the command line."""
    # Use the development settings unless the environment already names a
    # module. A server must set DJANGO_SETTINGS_MODULE explicitly.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


# ── Script entry point ────────────────────────────────────────────────

if __name__ == "__main__":
    main()
