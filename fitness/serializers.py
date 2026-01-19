from rest_framework import serializers
from .models import DietPlan, Meal, Supplement, BodyPart, Exercise, DailyTracker


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'meal_type', 'name', 'description', 'calories', 'protein', 'carbs', 'fat']


class DietPlanSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)
    
    class Meta:
        model = DietPlan
        fields = [
            'id', 'category', 'age_group', 'gender', 
            'height_min', 'height_max', 'weight_min', 'weight_max',
            'title', 'description',
            'total_calories', 'total_protein', 'total_carbs', 'total_fat',
            'meals', 'created_at'
        ]


class SupplementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplement
        fields = ['id', 'name', 'description', 'benefits']


class ExerciseSerializer(serializers.ModelSerializer):
    body_part_name = serializers.CharField(source='body_part.get_name_display', read_only=True)
    
    class Meta:
        model = Exercise
        fields = ['id', 'body_part', 'body_part_name', 'name', 'target_zone', 'description']


class BodyPartSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True)
    
    class Meta:
        model = BodyPart
        fields = ['id', 'name', 'description', 'exercises']


class DailyTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyTracker
        fields = ['id', 'date', 'attendance', 'diet_followed', 'workout_completed', 'notes', 'created_at']