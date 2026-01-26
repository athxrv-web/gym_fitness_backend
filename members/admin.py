"""
Members Admin
"""
from django.contrib import admin
from .models import Member, MemberAttendance, MembershipPlan


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'gym', 'status', 'membership_end_date', 'created_at']
    list_filter = ['status', 'gender', 'gym', 'created_at']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'age', 'gender', 'phone', 'email', 'address', 'photo')
        }),
        ('Physical Info', {
            'fields': ('height', 'weight')
        }),
        ('Membership', {
            'fields': ('gym', 'join_date', 'membership_type', 'membership_fee',
                      'membership_start_date', 'membership_end_date', 'status')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Health', {
            'fields': ('medical_conditions',)
        }),
        ('Meta', {
            'fields': ('created_by', 'created_at', 'updated_at')
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