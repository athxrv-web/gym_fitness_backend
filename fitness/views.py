from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DietPlan, Meal, Supplement, BodyPart, Exercise, DailyTracker
from .serializers import (
    DietPlanSerializer, MealSerializer, SupplementSerializer,
    BodyPartSerializer, ExerciseSerializer, DailyTrackerSerializer
)


class DietPlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint for diet plans
    """
    queryset = DietPlan.objects.all()
    serializer_class = DietPlanSerializer
    filterset_fields = ['category', 'age_group', 'gender']
    search_fields = ['title', 'description']
    
    @action(detail=False, methods=['get'])
    def find_plan(self, request):
        """Find diet plan based on user input"""
        category = request.query_params.get('category')
        age = request.query_params.get('age')
        gender = request.query_params.get('gender')
        height = request.query_params.get('height')
        weight = request.query_params.get('weight')
        
        if not all([category, age, gender, height, weight]):
            return Response(
                {"error": "Missing parameters"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            age = int(age)
            height = int(height)
            weight = int(weight)
        except ValueError:
            return Response(
                {"error": "Invalid number format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if 18 <= age <= 36:
            age_group = '18-36'
        elif 36 < age <= 60:
            age_group = '36-60'
        else:
            return Response(
                {"error": "Age must be between 18 and 60"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plans = DietPlan.objects.filter(
            category=category,
            age_group=age_group,
            gender=gender,
            height_min__lte=height,
            height_max__gte=height,
            weight_min__lte=weight,
            weight_max__gte=weight
        )
        
        if not plans.exists():
            return Response(
                {"error": "No matching diet plan found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)


class SupplementViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for supplements"""
    queryset = Supplement.objects.all()
    serializer_class = SupplementSerializer
    search_fields = ['name', 'description', 'benefits']


class BodyPartViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for body parts"""
    queryset = BodyPart.objects.all()
    serializer_class = BodyPartSerializer
    search_fields = ['name']


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for exercises"""
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    filterset_fields = ['body_part', 'target_zone']
    search_fields = ['name', 'target_zone', 'description']


class DailyTrackerViewSet(viewsets.ModelViewSet):
    """API endpoint for daily tracker"""
    queryset = DailyTracker.objects.all()
    serializer_class = DailyTrackerSerializer
    filterset_fields = ['date', 'attendance', 'diet_followed', 'workout_completed']
    ordering_fields = ['date']
    ordering = ['-date']