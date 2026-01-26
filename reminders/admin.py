"""
Reminders Admin
"""
from django.contrib import admin
from .models import Reminder


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['member', 'reminder_type', 'due_date', 'status', 'sent_at']
    list_filter = ['status', 'reminder_type', 'gym', 'created_at']
    search_fields = ['member__name', 'member__phone', 'message']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']