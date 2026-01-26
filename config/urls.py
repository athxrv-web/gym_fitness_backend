from django.contrib import admin
from django.urls import path, include
# 👇 YE DO LINES MISSING THI (Inhe Add Karo)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 👇 YE HAI ASLI LOGIN KA RASTA (Iske bina login nahi hoga)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Tumhare baaki raste (Jo pehle se wahan honge)
    path('api/members/', include('members.urls')),
    path('api/fitness/', include('fitness.urls')),
    path('api/payments/', include('payments.urls')),
    # ... baaki sab same rehne do
]