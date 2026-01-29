"""
Members Serializers
Optimized for Flutter Frontend & Crash Prevention
"""
from rest_framework import serializers
from .models import Member, MemberAttendance, MembershipPlan
from datetime import date

class MemberSerializer(serializers.ModelSerializer):
    # Read-only fields (Calculated from Model)
    days_remaining = serializers.ReadOnlyField()
    is_expiring_soon = serializers.ReadOnlyField()
    
    # Explicitly map 'profile_image' to handle file uploads correctly
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Member
        fields = [
            'id', 'name', 'phone', 'email', 
            'gender', 'age', 'height', 'weight',
            'profile_image', # Fixed name match with Model
            'membership_type', 'membership_fee',
            'join_date', 'membership_start_date', 'membership_end_date',
            'is_active',
            'days_remaining', 'is_expiring_soon',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'days_remaining', 'is_expiring_soon']

    # 🛡️ THE MAGIC FIX (Empty String Handler)
    def to_internal_value(self, data):
        """
        Ye function Frontend se aane wale data ko clean karta hai.
        Agar Flutter se Age/Fee/Weight empty string ("") aata hai, 
        toh ye usse None (Null) bana deta hai taaki Error na aaye.
        """
        # Data mutable banao (QueryDict fix)
        if hasattr(data, '_mutable'):
            data._mutable = True
            
        # List of fields jo Number hone chahiye
        number_fields = ['age', 'weight', 'height', 'membership_fee']
        
        for field in number_fields:
            if field in data and data[field] == "":
                data[field] = None
        
        # Email agar empty hai toh None karo (Unique constraint fix)
        if 'email' in data and data['email'] == "":
            data['email'] = None
            
        return super().to_internal_value(data)

    def validate(self, data):
        """Check Logic: End Date should be after Start Date"""
        if 'membership_start_date' in data and 'membership_end_date' in data:
            if data['membership_end_date'] < data['membership_start_date']:
                raise serializers.ValidationError("End date cannot be before start date.")
        return data


class MemberListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list view (Fast Loading)"""
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = Member
        fields = ['id', 'name', 'phone', 'is_active', 'membership_type', 
                 'membership_end_date', 'days_remaining', 'profile_image']


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