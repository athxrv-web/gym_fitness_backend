"""
Members Admin
Optimized to match Model Fields exactly
"""
from django.contrib import admin
from .models import Member, MemberAttendance, MembershipPlan

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    # ✅ Fixed: 'status' -> 'is_active'
    list_display = ['name', 'phone', 'gym', 'is_active', 'membership_end_date', 'created_at']
    list_filter = ['is_active', 'gender', 'gym', 'created_at']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Personal Info', {
            # ✅ Fixed: 'photo' -> 'profile_image'
            'fields': ('name', 'age', 'gender', 'phone', 'email', 'profile_image')
        }),
        ('Physical Info', {
            'fields': ('height', 'weight')
        }),
        ('Membership', {
            # ✅ Fixed: 'status' -> 'is_active'
            'fields': ('gym', 'join_date', 'membership_type', 'membership_fee',
                      'membership_start_date', 'membership_end_date', 'is_active')
        }),
        # Note: Medical/Emergency fields tabhi dikhenge agar Model me honge.
        # Agar Model me nahi hain toh ye lines hata dena.
        ('Meta', {
            'fields': ('created_at', 'updated_at') 
            # 'created_by' hata diya kyunki ye aksar model me miss ho jata hai
        }),
    )

@admin.register(MemberAttendance)
class MemberAttendanceAdmin(admin.ModelAdmin):
    list_display = ['member', 'gym', 'check_in_time', 'check_out_time']
    list_filter = ['gym', 'check_in_time']
    search_fields = ['member__name', 'member__phone']
    date_hierarchy = 'check_in_time'

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'gym', 'duration', 'price', 'is_active', 'created_at']
    list_filter = ['gym', 'duration', 'is_active']
    search_fields = ['name']