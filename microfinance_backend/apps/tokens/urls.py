from django.urls import path, include
from rest_framework.routers import DefaultRouter
#from apps.tokens.views import ReferralViewSet # <-- This line will now fail

router = DefaultRouter()
#router.register(r'referrals', ReferralViewSet)

#urlpatterns = [
#    path('', include(router.urls)), # <-- This implicitly uses ReferralViewSet
#]
# apps/telegram/views.py

from django.views.decorators.csrf import csrf_exempt # This line should be here
# ... other imports ...

@csrf_exempt # This decorator should be directly above your telegram_webhook function
def telegram_webhook(request):
    # ... rest of your view function ...
    return None 
# microfinance_backend/apps/telegram/urls.py

from django.urls import path
from apps.tokens import views # Recommended: relative import

urlpatterns = [ # <-- THIS LINE MUST NOT BE COMMENTED OUT
    path('', views.telegram_webhook, name='telegram_webhook'),
]
# microfinance_backend/apps/telegram/urls.py

from django.urls import path
from apps.tokens import views

app_name = 'telegram' # Optional: for namespacing URLs

urlpatterns = [
    # This maps /webhook/ relative to wherever 'telegram.urls' is included
    path('webhook/', views.telegram_webhook, name='telegram_webhook'),
]