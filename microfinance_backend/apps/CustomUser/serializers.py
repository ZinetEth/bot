# apps/CustomUser/serializers.py
from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    Used for converting CustomUser instances to JSON and vice-versa.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'telegram_id', 'phone_number', 'referral_code', 'referred_by', 'is_kyc_verified', 'mifos_client_id', 'password']
        read_only_fields = ['id', 'referral_code', 'referred_by', 'is_kyc_verified', 'mifos_client_id']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': False},
            'email': {'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance