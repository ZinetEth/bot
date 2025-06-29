from django.urls import path
from apps.CustomUser import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('check/', views.check_user_exists, name='check_user_exists'),
]
# This file defines the URL patterns for the CustomUser app.
# It includes paths for user registration and checking if a user exists.
# microfinance_backend/apps/CustomUser/urls.py