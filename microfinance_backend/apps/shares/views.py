from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import SharePurchase, Commission
from .serializers import SharePurchaseSerializer, CommissionSerializer
from apps.CustomUser.permissions import IsAdmin, IsStaff, IsAuditor

class SharePurchaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SharePurchase.objects.all().select_related('user', 'transaction')
    serializer_class = SharePurchaseSerializer
    permission_classes = [IsAuthenticated, (IsAdmin | IsStaff | IsAuditor)] # Admin, Staff, Auditor can view

    def get_queryset(self):
        # Allow regular users to see only their own share purchases
        if self.request.user.role not in ['ADMIN', 'STAFF', 'AUDITOR']:
            return self.queryset.filter(user=self.request.user)
        return self.queryset

class CommissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Commission.objects.all().select_related('payer', 'receiver', 'share_purchase')
    serializer_class = CommissionSerializer
    permission_classes = [IsAuthenticated, (IsAdmin | IsAuditor)] # Only Admin or Auditor can view commissions

    def get_queryset(self):
        # Allow regular users to see only commissions they received
        if self.request.user.role not in ['ADMIN', 'AUDITOR']:
            return self.queryset.filter(receiver=self.request.user)
        return self.queryset