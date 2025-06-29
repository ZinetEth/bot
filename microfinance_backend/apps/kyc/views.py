from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import KYCProfile
from .serializers import KYCProfileSerializer, KYCApprovalSerializer
from apps.CustomUser.permissions import IsAdmin, IsStaff
from apps.CustomUser.serializers import CustomUserSerializer
from django.utils import timezone

class KYCProfileViewSet(viewsets.ModelViewSet):
    queryset = KYCProfile.objects.all().select_related('user', 'created_by', 'approved_by')
    serializer_class = KYCProfileSerializer
    permission_classes = [IsAuthenticated] # Base permission, specific actions will have more roles

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsStaff] # Staff can create/update
        elif self.action in ['approve', 'reject']:
            self.permission_classes = [IsAuthenticated, IsAdmin] # Only Admin can approve/reject
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated, (IsAdmin | IsStaff)] # Admin or Staff can list/retrieve
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status='PENDING')

    def perform_update(self, serializer):
        # Allow staff to update their own entries if status is PENDING or REJECTED
        # Admins can update any entry
        instance = self.get_object()
        if self.request.user.role == 'STAFF' and instance.created_by != self.request.user:
            return Response({"detail": "You do not have permission to edit this KYC profile."}, 
                            status=status.HTTP_403_FORBIDDEN)
        if self.request.user.role == 'STAFF' and instance.status == 'APPROVED':
            return Response({"detail": "Approved KYC profiles cannot be updated by staff."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer.save(updated_at=timezone.now())

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        kyc_profile = self.get_object()
        serializer = KYCApprovalSerializer(data={'status': 'APPROVED'})
        serializer.is_valid(raise_exception=True)
        kyc_profile.status = 'APPROVED'
        kyc_profile.approved_by = request.user
        kyc_profile.rejection_reason = None
        kyc_profile.save()
        return Response(self.get_serializer(kyc_profile).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        kyc_profile = self.get_object()
        serializer = KYCApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rejection_reason = serializer.validated_data.get('rejection_reason', '')
        
        if not rejection_reason:
            return Response({"detail": "Rejection reason is required when rejecting a KYC profile."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        kyc_profile.status = 'REJECTED'
        kyc_profile.approved_by = request.user
        kyc_profile.rejection_reason = rejection_reason
        kyc_profile.save()
        return Response(self.get_serializer(kyc_profile).data)