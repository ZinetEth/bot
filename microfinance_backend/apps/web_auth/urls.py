# C:\Users\u\Desktop\New folder\microfinance_backend\apps\web_auth\urls.py

from django.urls import path
from django.contrib.auth import views as auth_views # Django's built-in auth views
from . import views # Your custom views

urlpatterns = [
    # Custom registration view
    path('register/', views.register_view, name='register'),

    # Django's built-in login/logout views
    # These views expect templates in 'registration/' directory by default
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'), # Redirects to login after logout
    
    # You can add password reset/change views here later if needed
    # path('password_change/', auth_views.PasswordChangeView.as_view(...), name='password_change'),
    # path('password_reset/', auth_views.PasswordResetView.as_view(...), name='password_reset'),
]