# apps/mlm/apps.py
from django.apps import AppConfig


class MlmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mlm' # This name must match how it's listed in INSTALLED_APPS (i.e., 'apps.mlm')
    verbose_name = "MLM (Multi-Level Marketing) Module" # Optional: A human-readable name for the app, useful in the Django admin interface 