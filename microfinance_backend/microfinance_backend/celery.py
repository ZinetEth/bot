# ymicrofinance_backend/_microfinance_backend/celery.py
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'microfinance_backendt.settings')

# Create a Celery application instance
app = Celery('microfinance_backendoject')

# Load task configuration from Django settings.
# The 'CELERY' namespace means all Celery-related settings
# will be prefixed with CELERY_ in settings.py (e.g., CELERY_BROKER_URL).
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed Django apps.
# Celery will look for a 'tasks.py' file in each app.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """
    A simple debug task to verify Celery is working.
    You can call this with `debug_task.delay()` from a Django shell.
    """
    print(f'Request: {self.request!r}')