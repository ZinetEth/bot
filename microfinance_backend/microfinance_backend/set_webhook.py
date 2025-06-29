# C:\Users\u\Desktop\New folder\microfinance_backend\set_webhook.py

import requests
from django.conf import settings
import os
import django

# Setup Django environment
# This is crucial so that settings.py can be accessed
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'microfinance_backend.settings')
django.setup()

WEBHOOK_URL = settings.WEBHOOK_URL
BOT_TOKEN = settings.BOT_TOKEN

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

def set_telegram_webhook():
    params = {
        'url': WEBHOOK_URL,
        # 'drop_pending_updates': True # Uncomment to clear any pending updates
    }
    print(f"Attempting to set webhook to: {WEBHOOK_URL}")
    try:
        response = requests.post(TELEGRAM_API_URL, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors
        result = response.json()
        if result.get('ok'):
            print(f"Webhook set successfully: {result.get('description')}")
        else:
            print(f"Failed to set webhook: {result.get('description')}")
    except requests.exceptions.RequestException as e:
        print(f"Error setting webhook: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    set_telegram_webhook()