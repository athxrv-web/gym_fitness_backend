from django.urls import path, include
from rest_framework.routers import DefaultRouter

# --- JWT Auth Imports (Login Token ke liye) ---
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# --- Views Imports (Sab yahan hone chahiye) ---
# Dhyan se dekho, yahan 'UserProfileViewSet' add kiya hai
from .views import (
    RegisterView,
    UserProfileViewSet,      # <--- Ye MISSING tha pehle
    DietPlanViewSet,
    MealViewSet,
    SupplementViewSet,
    BodyPartViewSet,
    ExerciseViewSet,
    DailyTrackerViewSet
)

# --- Router Setup ---
router = DefaultRouter()

# 1. User Management (Naya Feature)
router.register(r'users', UserProfileViewSet) 

# 2. Diet Features
router.register(r'diet-plans', DietPlanViewSet)
router.register(r'meals', MealViewSet)
router.register(r'supplements', SupplementViewSet)

# 3. Workout Features
router.register(r'body-parts', BodyPartViewSet)
router.register(r'exercises', ExerciseViewSet)

# 4. Tracker
router.register(r'tracker', DailyTrackerViewSet)

# --- URL Patterns ---
urlpatterns = [
    # API Router URLs
    path('', include(router.urls)),

    # Authentication Endpoints
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]