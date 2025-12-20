from django.apps import AppConfig


class UsersConfig(AppConfig):
<<<<<<< HEAD
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

=======
    """
    App configuration for the Users module.
    Loads signals on app startup.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        # Import signals so Django can register them
        from . import signals  # noqa
>>>>>>> feature/backend-api
