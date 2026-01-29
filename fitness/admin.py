"""
Fitness Admin Configuration
"""
from django.contrib import admin
from .models import User, Gym, ActivityLog

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'gym']
    search_fields = ['email', 'first_name', 'last_name', 'phone']

@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    # 'subscription_active' hata diya kyunki wo model me nahi hai
    list_display = ['name', 'owner', 'city', 'phone', 'whatsapp_enabled'] 
    list_filter = ['city', 'whatsapp_enabled']
    search_fields = ['name', 'phone','email']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'gym', 'created_at']
    list_filter = ['action', 'gym']
    search_fields = ['user__email', 'description']
    readonly_fields = ['created_at', 'ip_address']