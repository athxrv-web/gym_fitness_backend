from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ✅ ADMIN LOGIN TOKEN (Iske bina Admin Login nahi hoga)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ✅ APP URLS (Members, Fitness, etc.)
    path('api/members/', include('members.urls')),
    path('api/fitness/', include('fitness.urls')),
    path('api/payments/', include('payments.urls')),
]

# --- 👇 AUTO ADMIN CREATOR (Bina Shell ke Admin Banayega) 👇 ---
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Ye script server start hote hi chalegi
    if User.objects.filter(username='admin').exists():
        user = User.objects.get(username='admin')
        user.set_password('admin123456')
        user.save()
        print("✅ ADMIN RESET: admin / admin123456")
    else:
        User.objects.create_superuser('admin', 'admin@gymfitness.com', 'admin123456')
        print("🆕 ADMIN CREATED: admin / admin123456")

except Exception as e:
    print(f"⚠️ Admin Check Skipped: {e}")
# ---------------------------------------------------------------