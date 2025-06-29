# apps/core/urls.py
from django.urls import path
from apps.core import views # Assuming your core views are in core/views.py

urlpatterns = [
    path('', views.home_view, name='home'), # This path handles the root of the 'core' app,
                                            # which becomes the project root in this setup
    # Add other paths for your core app here, e.g.:
    # path('about/', views.about_view, name='about'),
    # path('contact/', views.contact_view, name='contact'),
]