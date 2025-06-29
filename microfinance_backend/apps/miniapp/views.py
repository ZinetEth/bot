# apps/miniapp/views.py
import json
import logging
import hmac
import hashlib
from urllib.parse import parse_qs, unquote

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db import transaction

from apps.CustomUser.models import CustomUser
from apps.telegram.models import TelegramUser # Assuming TelegramUser model is in apps.telegram

logger = logging.getLogger(__name__)

def validate_telegram_init_data(init_data_raw: str, bot_token: str) -> tuple[bool, dict | None]:
    """
    Validates Telegram WebApp initData using HMAC-SHA256.
    Returns (is_valid, parsed_data_dict)
    """
    logger.info(f"--- validate_telegram_init_data START ---")
    logger.info(f"Raw InitData received by validator (first 200 chars): {init_data_raw[:200]}...")
    # For debugging, showing part of the token is useful. In production, avoid logging full tokens.
    logger.info(f"Using bot_token for validation (first 10 chars): {bot_token[:10]}...") 

    if not init_data_raw:
        logger.warning("InitData validation failed: init_data_raw is empty.")
        return False, None

    # parse_qs returns a dictionary where values are lists (even for single values).
    # We convert them to single strings here.
    parsed_params_lists = parse_qs(init_data_raw)
    parsed_params = {k: v[0] for k, v in parsed_params_lists.items()}

    if 'hash' not in parsed_params:
        logger.warning("InitData validation failed: 'hash' parameter missing.")
        return False, None

    received_hash = parsed_params.pop('hash') # Remove hash from params for validation

    # Collect parameters for hash calculation, excluding 'hash' itself and 'query_id'
    # Parameters must be sorted alphabetically by key
    data_check_string_parts = []
    for key in sorted(parsed_params.keys()):
        # Values from parse_qs are already URL-decoded.
        # No need to call unquote again here.
        data_check_string_parts.append(f"{key}={parsed_params[key]}") 
    
    data_check_string = "\n".join(data_check_string_parts)

    logger.info(f"Backend constructed data_check_string: '{data_check_string}'")
    logger.info(f"Backend received hash from client: {received_hash}")

    # --- CRITICAL CORRECTION: Secret Key Derivation ---
    # The secret_key is HMAC-SHA256 of "WebAppData" using the bot_token as the key.
    try:
        secret_key = hmac.new(
            key="WebAppData".encode('utf-8'),
            msg=bot_token.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        logger.info("Secret key derived successfully.")
    except Exception as e:
        logger.error(f"Error deriving secret key: {e}")
        return False, None

    # Calculate HMAC-SHA256 hash of the data_check_string using the derived secret_key
    calculated_hash = hmac.new(
        key=secret_key, # Use the correctly derived secret_key (bytes)
        msg=data_check_string.encode('utf-8'), # The string to hash
        digestmod=hashlib.sha256
    ).hexdigest() # Convert to hexadecimal string for comparison

    logger.info(f"Backend calculated hash: {calculated_hash}")

    if calculated_hash == received_hash:
        logger.info("Telegram InitData validated successfully. Hashes Match!")
        
        # Prepare the data to return
        validated_data_for_return = parsed_params.copy() 

        # Parse 'user' field if present and valid JSON
        if 'user' in validated_data_for_return:
            try:
                # The 'user' value is a JSON string which needs to be parsed into a Python dict.
                user_data = json.loads(validated_data_for_return['user'])
                validated_data_for_return['user_data'] = user_data 
                # Optionally remove the original 'user' string key after parsing to avoid redundancy
                # del validated_data_for_return['user'] 
                logger.info(f"Successfully parsed 'user' data: {user_data.get('id')}")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse 'user' data from initData as JSON: {validated_data_for_return['user']}")
                validated_data_for_return['user_data'] = None # Explicitly set to None on error
        else:
            validated_data_for_return['user_data'] = None # Ensure user_data is always present as None if no 'user' field

        logger.info(f"Validated InitData user ID: {validated_data_for_return.get('user_data', {}).get('id', 'N/A')}")
        logger.info(f"--- validate_telegram_init_data END (Valid) ---")
        return True, validated_data_for_return
    else:
        logger.warning(f"InitData validation failed: Hashes do not match. Calculated: {calculated_hash}, Received: {received_hash}")
        logger.warning(f"Check string used for calculation: '{data_check_string}'")
        logger.warning(f"--- validate_telegram_init_data END (Invalid) ---")
        return False, None


# --- Django Views ---

def miniapp_view(request):
    """
    Serves the main HTML file for the Telegram Mini App.
    """
    return render(request, 'miniapp/index.html')

@csrf_exempt # API endpoint for Mini App, needs csrf_exempt for external calls
@require_http_methods(["POST"])
def miniapp_api_register(request):
    """
    Handles user registration/linking from the Mini App.
    Expects telegram_id, phone_number, and optional referral_code.
    """
    logger.info("--- miniapp_api_register START ---")
    
    # InitData is typically sent in the 'Authorization' header as a Bearer token
    # or a custom header like 'X-Telegram-Init-Data'.
    # You need to confirm how your frontend is sending it.
    # If it's in the JSON body, you'll get it from request.body.
    # Let's assume for now it's a custom header as that's common for InitData.
    # If your frontend sends it in the JSON body, you'll need to adapt this part.
    init_data_raw = request.headers.get('microfinance_backend-Telegram-Init-Data') 
    
    # If frontend sends it in JSON body (as previously discussed for status endpoint)
    if not init_data_raw:
        try:
            data_from_body = json.loads(request.body.decode('utf-8'))
            init_data_raw = data_from_body.get('initData')
            logger.info("InitData found in request body.")
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload or no InitData in body for register endpoint.")
            return HttpResponseBadRequest("Invalid JSON payload or InitData missing.")
    
    if not init_data_raw:
        logger.warning("No InitData received for registration.")
        return HttpResponseBadRequest("InitData is required.")

    # Ensure bot token is available
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not configured in Django settings.")
        return JsonResponse({"error": "Server configuration error"}, status=500)

    is_valid, validated_init_data = validate_telegram_init_data(init_data_raw, settings.TELEGRAM_BOT_TOKEN)

    if not is_valid:
        logger.warning(f"Registration attempt with invalid Telegram InitData. Validation result: {is_valid}")
        return HttpResponseForbidden("Unauthorized: Invalid Telegram InitData")

    # Ensure the user ID from initData matches the one sent in the body (if applicable)
    telegram_id_from_init_data = validated_init_data.get('user_data', {}).get('id')

    try:
        # Assuming the main data for registration (phone_number, referral_code) is in the JSON body
        data = json.loads(request.body.decode('utf-8'))
        # Get telegram_id from the body as well, for comparison. This is a common practice.
        telegram_id_from_body = data.get('telegram_id') 
        phone_number = data.get('phone_number')
        referral_code_input = data.get('referral_code')

        if not phone_number:
            logger.warning("Phone number is missing in registration request.")
            return JsonResponse({"error": "Phone number is required."}, status=400)
        
        # Cross-check Telegram ID from InitData with the one from the request body
        # This adds an extra layer of security against forging the body's telegram_id
        if telegram_id_from_init_data is None or telegram_id_from_init_data != telegram_id_from_body:
            logger.error(f"Mismatch Telegram ID: InitData ({telegram_id_from_init_data}), Body ({telegram_id_from_body})")
            return HttpResponseForbidden("Unauthorized: Telegram ID mismatch or missing.")

        with transaction.atomic():
            # Find or create CustomUser based on phone_number
            custom_user, custom_user_created = CustomUser.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'username': f'telegram_user_{telegram_id_from_body}', # Create a unique username
                    'telegram_id': telegram_id_from_body, # Link telegram ID directly to custom user
                    # Consider adding a password handling strategy (e.g., set_unusable_password())
                }
            )

            if custom_user_created:
                logger.info(f"New CustomUser created for phone {phone_number} and Telegram ID {telegram_id_from_body}")
            else:
                # If user already exists, ensure their telegram_id is linked
                if not custom_user.telegram_id:
                    custom_user.telegram_id = telegram_id_from_body
                    custom_user.save()
                logger.info(f"Existing CustomUser {custom_user.id} linked/updated with Telegram ID {telegram_id_from_body}")
            
            message = "Registration successful! Your account is linked." # Default success message
            
            # Handle referral code if provided and CustomUser was new or not yet referred
            if referral_code_input and not custom_user.referred_by: 
                try:
                    referrer = CustomUser.objects.get(referral_code=referral_code_input)
                    if referrer.id != custom_user.id: # A user cannot refer themselves
                        custom_user.referred_by = referrer
                        custom_user.save()
                        logger.info(f"User {custom_user.username} referred by {referrer.username}")
                        message = "Registration successful! Your account is linked and referral applied."
                    else:
                        message = "Registration successful, but you cannot refer yourself."
                except CustomUser.DoesNotExist:
                    logger.warning(f"Invalid referral code '{referral_code_input}' provided during registration for {custom_user.username}")
                    message = "Registration successful! Your account is linked, but referral code was invalid."
            
            # Ensure TelegramUser exists and is linked to the CustomUser
            telegram_user, telegram_user_created = TelegramUser.objects.update_or_create(
                user_id=telegram_id_from_body, # Telegram's user ID as the identifier
                defaults={
                    'first_name': validated_init_data.get('user_data', {}).get('first_name'),
                    'last_name': validated_init_data.get('user_data', {}).get('last_name'),
                    'username': validated_init_data.get('user_data', {}).get('username'),
                    'language_code': validated_init_data.get('user_data', {}).get('language_code'),
                    'linked_custom_user': custom_user, # Link the CustomUser instance
                }
            )
            logger.info(f"TelegramUser {telegram_user.user_id} updated/created for custom user {custom_user.id}")
            
            logger.info(f"User registration/linking process completed for Telegram ID {telegram_id_from_body}")
            
            return JsonResponse({
                "success": True,
                "message": message, 
                "custom_user_id": custom_user.id,
                "telegram_user_id": telegram_user.user_id, 
                "created": custom_user_created, # True if new CustomUser was created
            })
                
    except json.JSONDecodeError:
        logger.error("Invalid JSON payload in miniapp_api_register.")
        return HttpResponseBadRequest("Invalid JSON payload.")
    except Exception as e:
        logger.exception("An unexpected error occurred during Mini App registration:")
        return JsonResponse({"error": "An internal server error occurred during registration."}, status=500)


@csrf_exempt # API endpoint for Mini App, needs csrf_exempt for external calls
@require_http_methods(["POST"])
def miniapp_api_status(request):
    """
    Provides the registration status and dashboard data for the Mini App.
    """
    logger.info("--- miniapp_api_status START ---")
    
    # Assuming InitData is sent in the 'X-Telegram-Init-Data' header
    init_data_raw = request.headers.get('microfinance_backend-Telegram-Init-Data')

    # Fallback: if not in header, check if it's sent in JSON body (common for POST requests)
    if not init_data_raw:
        try:
            data_from_body = json.loads(request.body.decode('utf-8'))
            init_data_raw = data_from_body.get('initData')
            logger.info("InitData found in request body for status endpoint.")
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload or no InitData in body for status endpoint.")
            return HttpResponseBadRequest("Invalid JSON payload or InitData missing.")
    
    if not init_data_raw:
        logger.warning("No InitData received for status check.")
        return HttpResponseBadRequest("InitData is required.")

    # Ensure bot token is available
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not configured in Django settings.")
        return JsonResponse({"error": "Server configuration error"}, status=500)

    is_valid, validated_init_data = validate_telegram_init_data(init_data_raw, settings.TELEGRAM_BOT_TOKEN)

    if not is_valid:
        logger.warning(f"Status check attempt with invalid Telegram InitData. Validation result: {is_valid}")
        return HttpResponseForbidden("Unauthorized: Invalid Telegram InitData")

    telegram_id_from_init_data = validated_init_data.get('user_data', {}).get('id')

    if not telegram_id_from_init_data:
        logger.warning("Telegram User ID not found in validated InitData for status check.")
        return JsonResponse({"error": "Telegram User ID missing from InitData."}, status=400)

    try:
        telegram_user = TelegramUser.objects.get(user_id=telegram_id_from_init_data)
        
        # Check if linked to CustomUser
        if telegram_user.linked_custom_user:
            custom_user = telegram_user.linked_custom_user
            logger.info(f"CustomUser {custom_user.id} found for Telegram ID {telegram_id_from_init_data}.")
            
            # --- Fetch dashboard data ---
            # Implement actual logic to fetch real share balance, referral count, KYC status etc.
            # Example placeholders:
            share_balance = "0.00 ETB" 
            referral_count = custom_user.referrals.count() # Count direct referrals
            is_registered = True # True because a linked_custom_user exists
            # kyc_status = get_user_kyc_status(custom_user) # If you have a KYC app/function

            return JsonResponse({
                "is_registered": is_registered,
                "share_balance": share_balance,
                "referral_count": referral_count,
                # "kyc_status": kyc_status, 
                "username": custom_user.username, # Example of data to return
                "phone_number": custom_user.phone_number,
                "telegram_username": telegram_user.username,
            })
        else:
            logger.info(f"Telegram user {telegram_id_from_init_data} found but not linked to CustomUser.")
            return JsonResponse({"is_registered": False})

    except TelegramUser.DoesNotExist:
        logger.info(f"Telegram user {telegram_id_from_init_data} not found in DB during status check (not yet registered).")
        return JsonResponse({"is_registered": False})
    except Exception as e:
        logger.exception("Error during Mini App status check:")
        return JsonResponse({"error": "An internal server error occurred during status check."}, status=500)

# This `status_view` seems to be a duplicate or an old version.
# You likely only need `miniapp_api_status`. Consider removing this if it's redundant.
@csrf_exempt
def status_view(request):
    logger.warning("status_view endpoint accessed. This might be a redundant view.")
    init_data = request.headers.get("X-Telegram-Init-Data") # Corrected header name
    # Ensure BOT_TOKEN is imported or passed from settings
    # This view doesn't explicitly use settings.TELEGRAM_BOT_TOKEN
    # which could lead to issues if BOT_TOKEN is not globally defined.
    # It's safer to pass settings.TELEGRAM_BOT_TOKEN
    if not init_data:
        return JsonResponse({'error': 'InitData missing'}, status=400)

    # Assuming BOT_TOKEN is defined somewhere accessible to this function,
    # but it's better to use settings.TELEGRAM_BOT_TOKEN as used in other views.
    # For now, I'll use a placeholder `settings.TELEGRAM_BOT_TOKEN`.
    if not validate_telegram_init_data(init_data, settings.TELEGRAM_BOT_TOKEN)[0]: # Only check is_valid bool
        return JsonResponse({'error': 'Unauthorized'}, status=403)

from django.shortcuts import render

def miniapp_view(request):
    return render(request, 'miniapp/index.html')
