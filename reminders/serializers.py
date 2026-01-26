"""
Reminders Serializers
"""
from rest_framework import serializers
from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True)
    member_phone = serializers.CharField(source='member.phone', read_only=True)
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'member', 'member_name', 'member_phone',
            'reminder_type', 'message', 'due_date', 'amount',
            'status', 'sent_at', 'delivery_status', 'error_message',
            'created_at'
        ]
        read_only_fields = ['id', 'status', 'sent_at', 'delivery_status', 'created_at']