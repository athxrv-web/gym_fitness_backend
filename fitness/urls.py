"""
Fitness URLs
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    GymDetailView, DashboardStatsView, ActivityLogListView
)

app_name = 'fitness'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profile & Gym
    path('profile/', ProfileView.as_view(), name='profile'),
    path('gym/', GymDetailView.as_view(), name='gym'),
    
    # Dashboard
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard'),
    path('activity-logs/', ActivityLogListView.as_view(), name='activity-logs'),
]