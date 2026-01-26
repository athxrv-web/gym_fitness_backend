"""
Members Serializers
"""
from rest_framework import serializers
from .models import Member, MemberAttendance, MembershipPlan


class MemberSerializer(serializers.ModelSerializer):
    days_remaining = serializers.ReadOnlyField()
    is_expiring_soon = serializers.ReadOnlyField()
    
    class Meta:
        model = Member
        fields = [
            'id', 'name', 'age', 'gender', 'phone', 'email', 'address',
            'height', 'weight', 'photo', 'join_date', 'membership_type',
            'membership_fee', 'membership_start_date', 'membership_end_date',
            'status', 'emergency_contact_name', 'emergency_contact_phone',
            'medical_conditions', 'days_remaining', 'is_expiring_soon',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MemberListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view"""
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = Member
        fields = ['id', 'name', 'phone', 'status', 'membership_type', 
                 'membership_end_date', 'days_remaining', 'photo']


class MemberAttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True)
    member_phone = serializers.CharField(source='member.phone', read_only=True)
    
    class Meta:
        model = MemberAttendance
        fields = ['id', 'member', 'member_name', 'member_phone', 
                 'check_in_time', 'check_out_time', 'notes']
        read_only_fields = ['id', 'check_in_time']


class MembershipPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = ['id', 'name', 'duration', 'duration_days', 'price', 
                 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']