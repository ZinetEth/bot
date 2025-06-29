from rest_framework import serializers
from apps.MLM.models import Referral
from apps.CustomUser.serializers import UserSerializer

class ReferralSerializer(serializers.ModelSerializer):
    referrer_details = UserSerializer(source='referrer', read_only=True)
    referee_details = UserSerializer(source='referee', read_only=True)

    class Meta:
        model = Referral
        fields = ['id', 'referrer', 'referrer_details', 'referee', 'referee_details', 'created_at', 'is_expired']
        read_only_fields = ['created_at', 'is_expired']