"""
Fitness Serializers
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Gym, ActivityLog


class GymSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gym
        fields = ['id', 'name', 'address', 'city', 'state', 'pincode', 
                 'phone', 'email', 'logo', 'whatsapp_enabled', 
                 'auto_reminders_enabled', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    gym_details = GymSerializer(source='gym', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone',
                 'role', 'gym', 'gym_details', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.Serializer):
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
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def create(self, validated_data):
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
        user.gym = gym
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = authenticate(email=email, password=password)
        
        if not user:
            raise serializers.ValidationError('Invalid email or password')
        
        if not user.is_active:
            raise serializers.ValidationError('Account is disabled')
        
        attrs['user'] = user
        return attrs


class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_name', 'action', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() if obj.user else 'System'