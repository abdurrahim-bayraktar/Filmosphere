#!/usr/bin/env python
<<<<<<< HEAD
=======
"""Django's command-line utility for administrative tasks."""
>>>>>>> feature/backend-api
import os
import sys


<<<<<<< HEAD
def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "filmosphere.settings")
    from django.core.management import execute_from_command_line

=======
def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
>>>>>>> feature/backend-api
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
<<<<<<< HEAD


=======
>>>>>>> feature/backend-api
