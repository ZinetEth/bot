from rest_framework import serializers
from .models import Transaction
from apps.CustomUser.serializers import UserSerializer

class TransactionSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    approved_by_details = UserSerializer(source='approved_by', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'user_details', 'amount', 'method', 'reference', 'status',
            'auto_posted', 'created_at', 'approved_by', 'approved_by_details',
            'approved_at', 'rejection_reason'
        ]
        read_only_fields = ['status', 'auto_posted', 'created_at', 'approved_by', 'approved_at', 'rejection_reason']

class TransactionApprovalSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[('APPROVED', 'Approved'), ('REJECTED', 'Rejected')])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)