"""
Reminders Serializers
Optimized for Reliability & Data Integrity
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
        read_only_fields = ['id', 'status', 'sent_at', 'delivery_status', 'error_message', 'created_at']

    # 🛡️ LOGIC: Amount Negative nahi hona chahiye
    def validate_amount(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Reminder amount cannot be negative.")
        return value

    # 🛡️ CRASH PROOFING: Handle Empty Strings
    def to_internal_value(self, data):
        """
        Clean data before validation.
        Converts empty strings to None to avoid Server Error 500.
        """
        if hasattr(data, '_mutable'):
            data._mutable = True
            
        # Agar numeric/date fields khali hain, toh None bana do
        fields_to_clean = ['amount', 'due_date']
        for field in fields_to_clean:
            if field in data and data[field] == "":
                data[field] = None
            
        return super().to_internal_value(data)