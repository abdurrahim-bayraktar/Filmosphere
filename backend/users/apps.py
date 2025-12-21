from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    App configuration for the Users module.
    Loads signals on app startup.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        # Import signals so Django can register them
        try:
            from . import signals  # noqa
        except ImportError:
            pass  # signals.py might not exist yet
