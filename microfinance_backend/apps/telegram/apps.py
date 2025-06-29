import logging
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)

# IMPORTANT:
# The python-telegram-bot Application instance should NOT be initialized here
# or in the ready() method if it causes AppRegistryNotReady errors.
# It should be initialized lazily or in a context where the Django app registry
# is guaranteed to be fully loaded (e.g., within a view, a management command,
# or a Celery task, after Django.setup() has completed).

# We will remove the get_telegram_application function from here to simplify
# this file and avoid any potential early imports or initialization issues.
# If you need to access the PTB Application object, you'll initialize it
# within the specific view/function that uses it, ensuring Django's apps are ready.


class TelegramConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.telegram'
    verbose_name = "Telegram Bot Integration"

    def ready(self):
        """
        This method is called when Django starts up and all apps are loaded.
        It's crucial to keep this method lightweight and avoid importing models
        or performing database operations directly, as the app registry might
        not be fully initialized yet.
        """
        # We will not perform any complex initialization here to avoid AppRegistryNotReady.
        # Any necessary setup related to python-telegram-bot (like setting webhook)
        # will be handled by a separate management command or view, ensuring Django is fully ready.
        logger.info("Telegram app is ready. AppConfig.ready() executed. No early PTB initialization.")

# Note: If you need to perform any specific setup that requires the Django app registry,
# it should be done in a context where the registry is guaranteed to be ready,      