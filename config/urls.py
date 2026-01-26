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
# --- AUTO ADMIN CREATOR (Paste at the bottom of urls.py) ---
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Agar 'admin' naam ka user pehle se hai -> Password Reset karo
    if User.objects.filter(username='admin').exists():
        user = User.objects.get(username='admin')
        user.set_password('admin123456')
        user.save()
        print("✅ Purane Admin ka Password Reset ho gaya: admin123456")

    # Agar koi user nahi hai -> Naya Admin banao
    else:
        User.objects.create_superuser('admin', 'admin@gymfitness.com', 'admin123456')
        print("✅ Naya Admin Ban Gaya: admin / admin123456")

except Exception as e:
    print(f"❌ Error in Admin Creation: {e}")
# -----------------------------------------------------------