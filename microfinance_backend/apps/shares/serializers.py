# apps/shares/serializers.py
from rest_framework import serializers
from apps.CustomUser.serializers import CustomUserSerializer # <-- CORRECTED: Import CustomUserSerializer

# You will define your Share models here later, e.g.:
# from .models import SharePurchase, Commission

class SharePurchaseSerializer(serializers.Serializer): # Placeholder for now
    """
    Placeholder serializer for SharePurchase.
    You will replace this with a ModelSerializer once SharePurchase model is defined.
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.CharField(max_length=50)
    # user = CustomUserSerializer(read_only=True) # Example of linking to CustomUser

class CommissionSerializer(serializers.Serializer): # Placeholder for now
    """
    Placeholder serializer for Commission.
    You will replace this with a ModelSerializer once Commission model is defined.
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField(max_length=20)
    # user = CustomUserSerializer(read_only=True) # Example of linking to CustomUser
