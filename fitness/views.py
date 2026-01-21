from django.shortcuts import render
from rest_framework import viewsets, filters, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
# --- IMPORTS (Sabse Upar) ---
from django.db.models import Sum
from datetime import date, timedelta
from .models import IOSMember

# --- Models ---
from .models import (
    DietPlan, 
    Meal, 
    Supplement, 
    BodyPart, 
    Exercise, 
    DailyTracker,
    UserProfile  # <--- Yahan Sahi Hai
)

# --- Serializers ---
from .serializers import (
    DietPlanSerializer, 
    MealSerializer, 
    SupplementSerializer,
    BodyPartSerializer, 
    ExerciseSerializer, 
    DailyTrackerSerializer,
    RegisterSerializer,
    UserProfileSerializer
)

# ============================================
#  1. AUTHENTICATION & USER MANAGEMENT
# ============================================

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
    # Search & Filter Settings
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'user__first_name', 'mobile_number']

    # Filter 1: Gym User vs Non-User
    @action(detail=False, methods=['get'], url_path='filter-type')
    def filter_by_type(self, request):
        user_type = request.query_params.get('type') # e.g., ?type=Gym User
        if user_type:
            users = self.queryset.filter(user_type=user_type)
            serializer = self.get_serializer(users, many=True)
            return Response(serializer.data)
        return Response({"error": "Type parameter missing"}, status=400)

    # Filter 2: Admin Dashboard (Total Money)
    @action(detail=False, methods=['get'], url_path='admin-dashboard')
    def admin_dashboard(self, request):
        today = date.today()
        current_month = today.month
        current_year = today.year

        # Total Collection Logic
        # 2. Admin Dashboard: Total Collection (App + iOS)
    @action(detail=False, methods=['get'], url_path='admin-dashboard')
    def admin_dashboard(self, request):
        today = date.today()
        current_month = today.month
        current_year = today.year

        # 1. App Users se kamayi
        app_collection = UserProfile.objects.filter(
            fees_paid_date__month=current_month,
            fees_paid_date__year=current_year
        ).aggregate(Sum('fees_paid_amount'))['fees_paid_amount__sum'] or 0

        # 2. iOS/Offline Users se kamayi (Naya Feature)
        ios_collection = IOSMember.objects.filter(
            joining_date__month=current_month,
            joining_date__year=current_year
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

        # Total Paisa
        total_money = app_collection + ios_collection

        # Active Users Count
        active_app_users = UserProfile.objects.filter(expiry_date__gte=today).count()
        ios_users = IOSMember.objects.count()

        return Response({
            "current_month": today.strftime("%B"),
            "total_collection": total_money,        # Owner khush!
            "app_users_revenue": app_collection,
            "ios_users_revenue": ios_collection,
            "total_active_users": active_app_users + ios_users
        })

    # Filter 3: Fees Reminder (Expiring Soon)
    @action(detail=False, methods=['get'], url_path='fees-reminders')
    def fees_reminders(self, request):
        today = date.today()
        warning_date = today + timedelta(days=5)

        due_users = UserProfile.objects.filter(
            expiry_date__lte=warning_date,
            fees_status='Paid'
        )
        
        serializer = self.get_serializer(due_users, many=True)
        return Response(serializer.data)

# ============================================
#  2. DIET & WORKOUT FEATURES (Existing)
# ============================================

class DietPlanViewSet(viewsets.ModelViewSet):
    queryset = DietPlan.objects.all()
    serializer_class = DietPlanSerializer
    
    @action(detail=False, methods=['get'], url_path='find-plan')
    def find_plan(self, request):
        age = request.query_params.get('age')
        gender = request.query_params.get('gender')
        category = request.query_params.get('category')
        
        if not all([age, gender, category]):
            return Response(
                {"error": "Please provide age, gender, and category"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        plans = DietPlan.objects.filter(
            gender__iexact=gender,
            category__iexact=category,
            age_group=self._get_age_group(int(age))
        )
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)

    def _get_age_group(self, age):
        if 18 <= age <= 36:
            return '18-36'
        elif 36 < age <= 60:
            return '36-60'
        return '18-36'

class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

class SupplementViewSet(viewsets.ModelViewSet):
    queryset = Supplement.objects.all()
    serializer_class = SupplementSerializer

class BodyPartViewSet(viewsets.ModelViewSet):
    queryset = BodyPart.objects.all()
    serializer_class = BodyPartSerializer

class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['body_part__name']

class DailyTrackerViewSet(viewsets.ModelViewSet):
    queryset = DailyTracker.objects.all()
    serializer_class = DailyTrackerSerializer