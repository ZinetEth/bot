# apps/shares/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views # Import the views from this app

router = DefaultRouter()
router.register(r'purchases', views.SharePurchaseViewSet, basename='share-purchase')
router.register(r'commissions', views.CommissionViewSet, basename='commission')

urlpatterns = [
    path('', include(router.urls)),
    # Add any other specific share-related URLs here if not using ViewSets
]
# This file defines the URL routing for the shares app, including SharePurchase and Commission endpoints.
# It uses Django REST Framework's DefaultRouter to automatically generate routes for the viewsets.      