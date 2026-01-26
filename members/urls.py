"""
Members URLs
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
    path('<uuid:pk>/', MemberDetailView.as_view(), name='member-detail'),
    path('<uuid:pk>/check-in/', MemberCheckInView.as_view(), name='check-in'),
    path('expiring/', ExpiringMembersView.as_view(), name='expiring'),
    path('expired/', ExpiredMembersView.as_view(), name='expired'),
    path('stats/', MemberStatsView.as_view(), name='stats'),
    
    # Attendance
    path('attendance/list/', MemberAttendanceListView.as_view(), name='attendance-list'),
    
    # Membership Plans
    path('plans/', MembershipPlanListCreateView.as_view(), name='plan-list'),
    path('plans/<uuid:pk>/', MembershipPlanDetailView.as_view(), name='plan-detail'),
]