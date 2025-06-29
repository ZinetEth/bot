import json
import logging
import requests
import hmac # Added for initData validation
import hashlib # Added for initData validation
from urllib.parse import parse_qs, unquote # Added for initData validation

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden # Added HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction

from .models import TelegramUser, BotInteractionLog
from apps.CustomUser.models import CustomUser # Import CustomUser for linking

logger = logging.getLogger(__name__)

# Correctly use TELEGRAM_BOT_TOKEN from settings
TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/"

def send_telegram_message(chat_id, text, reply_markup=None):
    """Sends a message back to the Telegram user."""
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML' # Use HTML for formatting like <b>, <code>
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup) # Telegram requires JSON string for reply_markup

    try:
        response = requests.post(TELEGRAM_API_URL + "sendMessage", json=payload)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        logger.info(f"Message sent to chat_id {chat_id}: {text[:50]}...")
        return response.json()
    except requests.exceptions.RequestException as e:
        # Log the full response content for 4xx errors to get Telegram's specific error message
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Error sending message to Telegram (chat_id: {chat_id}): {e}. Response content: {e.response.text}")
        else:
            logger.error(f"Error sending message to Telegram (chat_id: {chat_id}): {e}")
        return None

def validate_telegram_init_data(init_data_raw, bot_token):
    """
    Validates Telegram WebApp initData using HMAC-SHA256.
    Returns (is_valid, parsed_data_dict)
    """
    if not init_data_raw:
        logger.warning("InitData validation failed: init_data_raw is empty.")
        return False, None

    # Parse query string parameters from init_data_raw
    # parse_qs returns lists, so we convert to single values
    parsed_params = {k: v[0] for k, v in parse_qs(init_data_raw).items()}

    if 'hash' not in parsed_params:
        logger.warning("InitData validation failed: 'hash' parameter missing.")
        return False, None

    received_hash = parsed_params.pop('hash') # Remove hash from params for validation

    # Collect parameters for hash calculation, excluding 'hash' itself
    data_check_string_parts = []
    for key in sorted(parsed_params.keys()):
        # Values must be URL-decoded before inclusion in data_check_string
        data_check_string_parts.append(f"{key}={unquote(parsed_params[key])}")
    data_check_string = "\n".join(data_check_string_parts)

    # Calculate secret_key using SHA256 of bot_token
    secret_key = hashlib.sha256(bot_token.encode('utf-8')).digest()

    # Calculate HMAC-SHA256 hash
    hmac_hash = hmac.new(secret_key, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()

    if hmac_hash == received_hash:
        logger.info("Telegram InitData validated successfully.")
        # Optionally parse 'user' field if present and valid JSON
        user_data = None
        if 'user' in parsed_params:
            try:
                user_data = json.loads(parsed_params['user'])
            except json.JSONDecodeError:
                logger.error("Failed to parse 'user' data from initData as JSON.")
        
        # Return the full parsed parameters including the user data if available
        # This dict contains all original parameters except 'hash', with 'user' potentially parsed
        parsed_params['user_data'] = user_data 
        return True, parsed_params
    else:
        logger.warning(f"InitData validation failed: Hashes do not match. Calculated: {hmac_hash}, Received: {received_hash}")
        return False, None

@csrf_exempt # Important for webhooks as they don't send CSRF tokens
@require_http_methods(["POST"]) # Only allow POST requests for webhooks
def telegram_webhook_view(request):
    """
    Handles incoming Telegram webhook updates.
    Parses the update, identifies the user, logs the interaction,
    and dispatches to appropriate command/message handlers.
    """
    try:
        update = json.loads(request.body.decode('utf-8'))
        logger.debug(f"Received Telegram update: {json.dumps(update, indent=2)}")

        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            from_user_data = message.get('from')
            text = message.get('text', '').strip() # Get message text, default to empty string

            if not from_user_data:
                logger.warning("Received update without 'from' user information. Ignoring.")
                return JsonResponse({"status": "ignored", "message": "No user info"}, status=200)

            # Ensure TelegramUser exists or create it
            with transaction.atomic():
                telegram_user, created = TelegramUser.objects.update_or_create(
                    user_id=from_user_data['id'],
                    defaults={
                        'first_name': from_user_data.get('first_name'),
                        'last_name': from_user_data.get('last_name'),
                        'username': from_user_data.get('username'),
                        'is_bot': from_user_data.get('is_bot', False),
                        'language_code': from_user_data.get('language_code'),
                    }
                )
            if created:
                logger.info(f"New Telegram user created: {telegram_user.username} ({telegram_user.user_id})")

            # Log the incoming message
            interaction_log = BotInteractionLog.objects.create(
                telegram_user=telegram_user,
                message_text=text
            )

            # --- Handle commands ---
            if text.startswith('/'):
                command_parts = text.split(' ', 1)
                command = command_parts[0].lower()
                args = command_parts[1] if len(command_parts) > 1 else ''

                # Update log with command used
                interaction_log.command_used = command
                interaction_log.save()

                if command == '/start':
                    response_text = (
                        f"Hello {telegram_user.first_name or 'there'}! Welcome to the Microfinance Bot.\n"
                        "I can help you manage your microfinance account.\n"
                        "Use /register to link your account or /help to see available commands."
                    )
                    send_telegram_message(chat_id, response_text)
                    interaction_log.response_text = response_text
                    interaction_log.save()

                elif command == '/help':
                    response_text = (
                        "Here are the commands you can use:\n"
                        "/start - Start interacting with the bot\n"
                        "/help - Show this help message\n"
                        "/register - Link your microfinance account and access the Mini App\n"
                        "/balance - Check your account balance (requires registration)\n"
                        "/loan_status - Check your loan status (requires registration)\n"
                        "/purchase_shares - Buy shares (opens Mini App)\n"
                        "/referrals - View your referral network and commissions\n"
                        "/contact - Get contact information"
                    )
                    send_telegram_message(chat_id, response_text)
                    interaction_log.response_text = response_text
                    interaction_log.save()

                elif command == '/register':
                    # The URL for your Mini App.
                    # IMPORTANT: Replace with your actual public domain or ngrok URL.
                    # Example: "https://your-public-domain.com/miniapp/"
                    # For local testing with ngrok, it would be your ngrok URL + /miniapp/
                    MINI_APP_URL = "https://e7d8-102-218-50-67.ngrok-free.app" # <-- **UPDATE THIS URL with your current ngrok URL**

                    reply_markup = {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "Register / Open Portal",
                                    "web_app": {"url": MINI_APP_URL}
                                }
                            ]
                        ]
                    }
                    response_text = "Tap the button below to register or access your customer portal:"
                    send_telegram_message(
                        chat_id,
                        response_text,
                        reply_markup=reply_markup
                    )
                    interaction_log.response_text = response_text
                    interaction_log.save()

                # Placeholder for other commands (e.g., /balance, /loan_status, /purchase_shares, /referrals, /contact)
                # These will be implemented in later steps, often interacting with the Mini App.
                else:
                    response_text = "Sorry, I don't understand that command. Type /help for a list of commands."
                    send_telegram_message(chat_id, response_text)
                    interaction_log.response_text = response_text
                    interaction_log.save()
            else:
                # Handle non-command messages
                response_text = f"I received your message: \"{text}\". If you need help, type /help."
                send_telegram_message(chat_id, response_text)
                interaction_log.response_text = response_text
                interaction_log.save()

        elif 'callback_query' in update:
            # Handle inline keyboard button presses (not Mini App launch buttons, those are handled by Telegram client)
            callback_query = update['callback_query']
            chat_id = callback_query['message']['chat']['id']
            data = callback_query['data']
            message_id = callback_query['message']['message_id']
            from_user_data = callback_query['from']

            # Acknowledge callback query to remove "loading" state on button
            requests.post(TELEGRAM_API_URL + "answerCallbackQuery", json={'callback_query_id': callback_query['id']})

            logger.info(f"Received callback query: {data} from user {from_user_data.get('id')}")

            # Example: Handle a simple button press
            if data == 'some_simple_action':
                response_text = "You pressed a simple button!"
                send_telegram_message(chat_id, response_text)
            # Add more `if/elif` conditions to handle different callback data
            # You might also edit the original message:
            # requests.post(TELEGRAM_API_URL + "editMessageText", json={
            #     'chat_id': chat_id,
            #     'message_id': message_id,
            #     'text': 'Message updated after button press!',
            #     'parse_mode': 'HTML'
            # })

        # Add more 'elif' conditions here to handle other update types
        # like 'edited_message', 'channel_post', 'inline_query', etc.
        # Check Telegram Bot API documentation for full 'Update' object structure.

        return JsonResponse({"status": "ok"})

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook request: {e}")
        return HttpResponseBadRequest("Invalid JSON payload")
    except Exception as e:
        logger.exception("Error processing Telegram webhook:") # Logs traceback for debugging
        return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)

def validate_telegram_init_data(init_data_raw, bot_token):
    """
    Validates Telegram WebApp initData using the official double HMAC-SHA256 method.
    Returns (is_valid, parsed_data_dict)
    """
    if not init_data_raw:
        logger.warning("InitData validation failed: init_data_raw is empty.")
        return False, None

    parsed_params = {k: v[0] for k, v in parse_qs(init_data_raw).items()}

    if 'hash' not in parsed_params:
        logger.warning("InitData validation failed: 'hash' parameter missing.")
        return False, None

    received_hash = parsed_params.pop('hash')  # Exclude 'hash' for validation

    # Build the data_check_string
    data_check_string_parts = []
    for key in sorted(parsed_params.keys()):
        data_check_string_parts.append(f"{key}={unquote(parsed_params[key])}")
    data_check_string = '\n'.join(data_check_string_parts)

    # STEP 1: Derive secret key from bot_token using HMAC
    secret_key = hmac.new(
        key="WebAppData".encode('utf-8'),
        msg=bot_token.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    # STEP 2: Final hash of the data_check_string
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Compare hashes
    if calculated_hash == received_hash:
        logger.info("✅ Telegram InitData validated successfully.")

        user_data = None
        if 'user' in parsed_params:
            try:
                user_data = json.loads(parsed_params['user'])
            except json.JSONDecodeError:
                logger.error("❌ Failed to parse 'user' from initData.")

        parsed_params['user_data'] = user_data
        return True, parsed_params
    else:
        logger.warning(
            f"❌ InitData validation failed:\n"
            f"Backend constructed data_check_string: '{data_check_string}'\n"
            f"Calculated hash: {calculated_hash}\n"
            f"Received hash: {received_hash}"
        )
        return False, None
@csrf_exempt
@require_http_methods(["POST"]) # Only allow POST requests for this endpoint
def miniapp_api_status(request):                            
    """
    API endpoint to check Mini App status and user registration.
    Expects Telegram WebApp initData in the request body or headers.
    """
    logger.info("--- miniapp_api_status START ---")

    # Assuming InitData is sent in the 'X-Telegram-Init-Data' header
    init_data_raw = request.headers.get('microfinance_backend-Telegram-Init-Data')

    # Fallback: if not in header, check if it's sent in JSON body (common for POST requests)
    if not init_data_raw:
        try:
            init_data_raw = json.loads(request.body.decode('utf-8')).get('init_data')
        except (json.JSONDecodeError, KeyError):
            return HttpResponseBadRequest("Missing or invalid init_data")

    # Validate the initData
    is_valid, parsed_data = validate_telegram_init_data(init_data_raw, settings.TELEGRAM_BOT_TOKEN)
    
    if not is_valid:
        return HttpResponseForbidden("Unauthorized: Invalid initData")

    # Simulate success response
    return JsonResponse({
        "is_registered": True,
        "share_balance": 10,
        "referral_count": 2
    })