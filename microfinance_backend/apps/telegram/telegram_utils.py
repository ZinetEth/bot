# C:\Users\u\Desktop\New folder\microfinance_backend\apps\telegram\telegram_utils.py

import requests
import json
from django.conf import settings # Make sure settings are imported to access TELEGRAM_BOT_TOKEN

# --- IMPORTANT: Ensure TELEGRAM_BOT_TOKEN is set in your Django settings.py ---
# Example in your project's settings.py:
# TELEGRAM_BOT_TOKEN = "YOUR_ACTUAL_BOT_TOKEN_HERE"
# Replace "YOUR_ACTUAL_BOT_TOKEN_HERE" with the token you got from BotFather.

TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"

def _make_telegram_api_call(method, params=None):
    """Helper function to make API calls to Telegram."""
    url = f"{TELEGRAM_API_URL}{method}"
    try:
        response = requests.post(url, json=params)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Telegram API call error for method {method}: {e}")
        # Log the full response for debugging if needed
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        return None

def send_telegram_message(chat_id, text, reply_markup=None, parse_mode='HTML'):
    """Sends a message to a Telegram chat."""
    params = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
    }
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)
    return _make_telegram_api_call('sendMessage', params)

def edit_telegram_message(chat_id, message_id, text, reply_markup=None, parse_mode='HTML'):
    """Edits an existing message in a Telegram chat."""
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': parse_mode,
    }
    if reply_markup:
        params['reply_markup'] = json.dumps(reply_markup)
    return _make_telegram_api_call('editMessageText', params)

def delete_telegram_message(chat_id, message_id):
    """Deletes a message in a Telegram chat."""
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
    }
    return _make_telegram_api_call('deleteMessage', params)

def answer_callback_query(callback_query_id, text=None, show_alert=False):
    """Sends a response to a callback query."""
    params = {
        'callback_query_id': callback_query_id,
    }
    if text:
        params['text'] = text
    if show_alert:
        params['show_alert'] = show_alert
    return _make_telegram_api_call('answerCallbackQuery', params)