"""
Members URLs
Fixed: Changed uuid:pk to int:pk to match Member Model ID type
"""
from django.urls import path
from .views import (
    MemberListCreateView, MemberDetailView, MemberCheckInView,
    MemberAttendanceListView, ExpiringMembersView, ExpiredMembersView,
    MembershipPlanListCreateView, MembershipPlanDetailView, MemberStatsView
)

app_name = 'members'

urlpatterns = [
    # Members
    path('', MemberListCreateView.as_view(), name='member-list'),
    
    # 🚨 FIX: <uuid:pk> ko <int:pk> kiya kyunki Member Model me ID Integer hai
    path('<int:pk>/', MemberDetailView.as_view(), name='member-detail'),
    path('<int:pk>/check-in/', MemberCheckInView.as_view(), name='check-in'),
    
    # Custom Lists
    path('expiring/', ExpiringMembersView.as_view(), name='expiring'),
    path('expired/', ExpiredMembersView.as_view(), name='expired'),
    path('stats/', MemberStatsView.as_view(), name='stats'),
    
    # Attendance
    path('attendance/list/', MemberAttendanceListView.as_view(), name='attendance-list'),
    
    # Membership Plans (Assuming Plans also use Integer IDs)
    path('plans/', MembershipPlanListCreateView.as_view(), name='plan-list'),
    path('plans/<int:pk>/', MembershipPlanDetailView.as_view(), name='plan-detail'),
]