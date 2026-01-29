from django.urls import path
from .views import (
    MemberListCreateView, MemberDetailView, MemberCheckInView,
    MemberAttendanceListView, ExpiringMembersView, ExpiredMembersView,
    MembershipPlanListCreateView, MembershipPlanDetailView, MemberStatsView,
    check_member_status # 👈 YE IMPORT ZAROORI HAI
)

app_name = 'members'

urlpatterns = [
    # --- ADMIN ROUTES (Token Required) ---
    path('', MemberListCreateView.as_view(), name='member-list'),
    path('<int:pk>/', MemberDetailView.as_view(), name='member-detail'),
    path('<int:pk>/check-in/', MemberCheckInView.as_view(), name='check-in'),
    
    path('expiring/', ExpiringMembersView.as_view(), name='expiring'),
    path('expired/', ExpiredMembersView.as_view(), name='expired'),
    path('stats/', MemberStatsView.as_view(), name='stats'),
    
    path('attendance/list/', MemberAttendanceListView.as_view(), name='attendance-list'),
    path('plans/', MembershipPlanListCreateView.as_view(), name='plan-list'),
    path('plans/<int:pk>/', MembershipPlanDetailView.as_view(), name='plan-detail'),
    
    # --- 👇 MEMBER LOGIN ROUTE (No Token Required) 👇 ---
    path('status/check/', check_member_status, name='check_member_status'),
]