"""
Fitness Serializers - Authentication & Gym Management
Optimized for Data Integrity & Security
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import transaction # 🛡️ For Atomic Transactions
from .models import User, Gym, ActivityLog

class GymSerializer(serializers.ModelSerializer):
    """Serializer for Gym Details"""
    class Meta:
        model = Gym
        fields = ['id', 'name', 'address', 'city', 'state', 'pincode', 
                 'phone', 'email', 'logo', 'whatsapp_enabled', 
                 'auto_reminders_enabled', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_logo(self, value):
        """Security: Limit logo file size to 2MB"""
        if value:
            limit = 2 * 1024 * 1024
            if value.size > limit:
                raise serializers.ValidationError('File too large. Size should not exceed 2 MiB.')
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User Profile"""
    gym_details = GymSerializer(source='gym', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone',
                 'role', 'gym', 'gym_details', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.Serializer):
    """
    Registration Logic with Atomic Transaction
    Creates User + Gym together safely.
    """
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    
    # Gym fields
    gym_name = serializers.CharField()
    gym_address = serializers.CharField()
    gym_city = serializers.CharField()
    gym_state = serializers.CharField()
    gym_pincode = serializers.CharField()
    gym_phone = serializers.CharField()
    
    def validate_email(self, value):
        # Case insensitive email check
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value.lower()
    
    def validate(self, attrs):
        # Strip whitespace from all string fields
        for key, value in attrs.items():
            if isinstance(value, str):
                attrs[key] = value.strip()
        return attrs

    def create(self, validated_data):
        # 🛡️ ATOMIC TRANSACTION: All or Nothing
        with transaction.atomic():
            # Extract gym data
            gym_data = {
                'name': validated_data.pop('gym_name'),
                'address': validated_data.pop('gym_address'),
                'city': validated_data.pop('gym_city'),
                'state': validated_data.pop('gym_state'),
                'pincode': validated_data.pop('gym_pincode'),
                'phone': validated_data.pop('gym_phone'),
                'email': validated_data['email'],
            }
            
            # Create user
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                phone=validated_data.get('phone'),
                role='GYM_OWNER'
            )
            
            # Create gym
            gym = Gym.objects.create(owner=user, **gym_data)
            
            # Link user to gym
            user.gym = gym
            user.save()
            
            return user


class LoginSerializer(serializers.Serializer):
    """Secure Login Validation"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email').lower().strip() # Normalize email
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), 
                                email=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include "email" and "password".')
            
        return attrs


class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_name', 'action', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() if obj.user else 'System'