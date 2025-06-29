# apps/miniapp/apps.py
from django.apps import AppConfig


class MiniappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.miniapp' # This name must match how it's listed in INSTALLED_APPS (i.e., 'apps.miniapp')
    verbose_name = "Mini App Integration"  # Optional: A human-readable name for the app, useful in the Django admin interface  