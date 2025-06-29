from rest_framework import serializers
from .models import KYCProfile
from apps.CustomUser.permissions import IsAdmin, IsStaff       
from apps.CustomUser.serializers import CustomUserSerializer
class KYCProfileSerializer(serializers.ModelSerializer):
    created_by_details =CustomUserSerializer(source='created_by', read_only=True)
    approved_by_details = CustomUserSerializer(source='approved_by', read_only=True)

    class Meta:
        model = KYCProfile
        fields = [
            'id', 'user', 'national_id_number', 'id_document', 'date_of_birth', 'address',
            'created_by', 'created_by_details', 'approved_by', 'approved_by_details', 'status',
            'created_at', 'updated_at', 'rejection_reason'
        ]
        read_only_fields = ['created_by', 'approved_by', 'status', 'created_at', 'updated_at']

class KYCApprovalSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=KYCProfile.STATUS_CHOICES)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)