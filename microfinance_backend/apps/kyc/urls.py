from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.kyc.views import KYCProfileViewSet

router = DefaultRouter()
router.register(r'kyc-profiles', KYCProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]


# This code defines the URL routing for the KYC (Know Your Customer) profiles in a Django application.
# It uses Django's REST framework to create a router that maps HTTP requests to the appropriate view