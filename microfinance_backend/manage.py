#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Add the 'apps' directory to the Python path
# This helps Django find apps located in the 'apps' subdirectory
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'apps'))

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'microfinance_backend.settings')
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

# This script is the entry point for running Django management commands.
# It sets up the environment and allows you to run commands like `python manage.py runserver    