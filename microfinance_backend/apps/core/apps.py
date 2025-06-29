from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core' # This name must match how it's listed in INSTALLED_APPS (i.e., 'apps.core')
    verbose_name = "Core Application"  # Optional: A human-readable name for the app, useful in the Django admin interface