#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess


def install_requirements():
    print("=> Installing requirements...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True, capture_output=True, text=True)
        print(result.stdout)
        print("=> Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print("=> Error installing requirements:")
        print(e.stderr)
        sys.exit(1)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.base')
    
    # Install the requirements **before** importing Django, unless we are running the server
    if os.environ.get('RUN_MAIN') != 'true':
        install_requirements()
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
