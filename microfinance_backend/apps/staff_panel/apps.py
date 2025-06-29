from django.apps import AppConfig


class StaffPanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.staff_panel' # This name must match how it's listed in INSTALLED_APPS
    verbose_name = "Staff Panel"