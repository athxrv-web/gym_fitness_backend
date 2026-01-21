from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DietPlan, Meal, Supplement, BodyPart, Exercise, DailyTracker, UserProfile

# --- AUTH ---
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        # Auto-create UserProfile
        UserProfile.objects.create(user=user)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'

# --- WORKOUT ---
class BodyPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyPart
        fields = '__all__'

class ExerciseSerializer(serializers.ModelSerializer):
    body_part_name = serializers.CharField(source='body_part.name', read_only=True)
    
    class Meta:
        model = Exercise
        # Video link & Target Area added here
        fields = ['id', 'name', 'body_part', 'body_part_name', 'target_area', 'video_link', 'instructions', 'image']

# --- DIET ---
class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'

class DietPlanSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)
    class Meta:
        model = DietPlan
        fields = '__all__'

class SupplementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplement
        fields = '__all__'

# --- TRACKER ---
class DailyTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyTracker
        fields = '__all__'