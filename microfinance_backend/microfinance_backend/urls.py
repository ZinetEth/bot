from django.contrib import admin
from django.urls import path, include
from apps.miniapp.views import miniapp_view  # 👈 Add this

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('apps.CustomUser.urls')),
    path('api/shares/', include('apps.shares.urls')),
    path('api/kyc/', include('apps.kyc.urls')),
    path('api/mifos-x/', include('apps.mifos_x.urls')),
    path('webhook/', include('apps.telegram.urls')),
    path('accounts/', include('apps.web_auth.urls')),
    path('miniapp/', include('apps.miniapp.urls')),

    # 👇 This adds the root URL that shows your Mini App
    path('', miniapp_view, name='home'),
]
