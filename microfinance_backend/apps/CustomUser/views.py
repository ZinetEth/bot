# apps/CustomUser/views.py
import json
import logging

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from django.shortcuts import get_object_or_404 # Useful for retrieving objects

from .models import CustomUser
from .serializers import CustomUserSerializer # Import your new serializer

# REMOVED INCORRECT IMPORTS:
# from apps.telegram.models import CustomUser # This is a duplicate and incorrect import
# from apps.kyc.models import KYCProfile # Not needed here yet
# from apps.telegram.models import Transaction # This model is not in apps.telegram.models

logger = logging.getLogger(__name__)

@api_view(['POST'])
def register_user(request):
    """
    Handles user registration via API using Django REST Framework.
    Supports creating a new CustomUser and linking Telegram ID/phone number.
    Handles optional referral code.
    """
    data = request.data # DRF automatically parses request.data for POST/PUT/PATCH

    # Ensure phone_number is provided
    phone_number = data.get('phone_number')
    if not phone_number:
        return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            # Check if a user with this phone number already exists
            try:
                user = CustomUser.objects.get(phone_number=phone_number)
                # If user exists, update their telegram_id if it's new
                telegram_id = data.get('telegram_id')
                if telegram_id and not user.telegram_id:
                    user.telegram_id = telegram_id
                    user.save()
                    logger.info(f"Existing user {phone_number} linked to Telegram ID {telegram_id}")
                
                # Serialize the existing user data to return
                serializer = CustomUserSerializer(user)
                return Response({"message": "User already registered.", "user": serializer.data}, status=status.HTTP_200_OK)

            except CustomUser.DoesNotExist:
                # If user does not exist, proceed with creating a new one
                serializer = CustomUserSerializer(data=data)
                if serializer.is_valid():
                    # Save the new user. The serializer's create method handles password and referral.
                    user = serializer.save()

                    # Handle referral logic if provided and user was newly created
                    referral_code_input = data.get('referral_code')
                    if referral_code_input and not user.referred_by: # Only apply if not already referred
                        try:
                            referrer = CustomUser.objects.get(referral_code=referral_code_input)
                            if referrer.id != user.id: # Prevent self-referral
                                user.referred_by = referrer
                                user.save()
                                logger.info(f"New user {user.username} referred by {referrer.username}")
                                message = "Registration successful! Your account is linked and referral applied."
                            else:
                                message = "Registration successful, but you cannot refer yourself."
                        except CustomUser.DoesNotExist:
                            logger.warning(f"Invalid referral code '{referral_code_input}' provided during registration for {user.username}")
                            message = "Registration successful! Your account is linked, but referral code was invalid."
                    else:
                        message = "Registration successful! Your account is linked."

                    return Response({"message": message, "user": serializer.data}, status=status.HTTP_201_CREATED)
                
                logger.error(f"Registration validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e: # This try-except block now correctly wraps the function logic
        logger.exception("Error during user registration:")
        return Response({"error": "An internal server error occurred during registration."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET']) # Changed to GET as per your urls.py
def check_user_exists(request):
    """
    Checks if a user exists based on Telegram ID or phone number.
    Uses query parameters for GET requests.
    """
    try: # <-- Added try block here
        telegram_id = request.query_params.get('telegram_id')
        phone_number = request.query_params.get('phone_number')

        if not telegram_id and not phone_number:
            return Response({"error": "Either telegram_id or phone_number is required."}, status=status.HTTP_400_BAD_REQUEST)

        user_exists = False
        user_data = None

        if telegram_id:
            try:
                user = CustomUser.objects.get(telegram_id=telegram_id)
                user_exists = True
                user_data = CustomUserSerializer(user).data
            except CustomUser.DoesNotExist:
                pass
        elif phone_number:
            try:
                user = CustomUser.objects.get(phone_number=phone_number)
                user_exists = True
                user_data = CustomUserSerializer(user).data
            except CustomUser.DoesNotExist:
                pass

        return Response({'exists': user_exists, 'user': user_data}, status=status.HTTP_200_OK)

    except Exception as e: # This is the line that was causing the syntax error
        logger.exception("Error during user existence check:")
        return Response({"error": "An internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)