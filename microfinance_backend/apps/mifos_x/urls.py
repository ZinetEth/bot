# microfinance_backend/apps/mifos_x/urls.py
from django.urls import path
from apps.mifos_x.views import MifosStatusView

urlpatterns = [
    path('status/', MifosStatusView.as_view(), name='mifos-status'),
]