# apps/telegram/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # This path handles the Telegram webhook.
    # The main project urls.py includes this at `path('webhook/', include('apps.telegram.urls'))`
    # So the full URL will be `yourdomain.com/webhook/`
    path('', views.telegram_webhook_view, name='telegram_webhook'), # Corrected function name
]
