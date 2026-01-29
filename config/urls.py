from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import LoginView   # 👈 CUSTOM LOGIN IMPORT

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ PROFESSIONAL LOGIN API (EMAIL + USERNAME WORKS)
    path('api/login/', LoginView.as_view(), name='login'),

    # ✅ REFRESH TOKEN
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ✅ APP URLS
    path('api/members/', include('members.urls')),
    path('api/fitness/', include('fitness.urls')),
    path('api/payments/', include('payments.urls')),
]