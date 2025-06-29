# apps/miniapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Serves the main HTML file for the Mini App (e.g., yourdomain.com/miniapp/)
    path('', views.miniapp_view, name='miniapp_home'),
    
    # API endpoint for Mini App registration (e.g., yourdomain.com/miniapp/api/register/)
    path('api/register/', views.miniapp_api_register, name='miniapp_api_register'),

    # API endpoint for Mini App status/dashboard data (e.g., yourdomain.com/miniapp/api/status/)
    path('api/status/', views.miniapp_api_status, name='miniapp_api_status'), # Corrected typo here

    # Add more API endpoints here as your Mini App grows (e.g., /api/shares/buy, /api/kyc/submit)
]
