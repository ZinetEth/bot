from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.MLM.models import Referral
from apps.MLM.serializers import ReferralSerializer
from apps.CustomUser.permissions import IsAdmin, IsAuditor

class ReferralViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Referral.objects.all().select_related('referrer', 'referee')
    serializer_class = ReferralSerializer
    permission_classes = [IsAuthenticated, (IsAdmin | IsAuditor)] # Only Admin or Auditor can view referrals