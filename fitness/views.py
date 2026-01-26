"""
Fitness Views - Authentication
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Gym, ActivityLog
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, 
    GymSerializer, ActivityLogSerializer
)


class RegisterView(generics.CreateAPIView):
    """Register new gym owner"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """User login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        # Log activity
        if user.gym:
            ActivityLog.objects.create(
                user=user,
                gym=user.gym,
                action='LOGIN',
                description=f'User {user.email} logged in',
                ip_address=request.META.get('REMOTE_ADDR')
            )
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login successful'
        })


class LogoutView(APIView):
    """User logout"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if request.user.gym:
            ActivityLog.objects.create(
                user=request.user,
                gym=request.user.gym,
                action='LOGOUT',
                description=f'User {request.user.email} logged out'
            )
        
        return Response({'message': 'Logout successful'})


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get/Update user profile"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class GymDetailView(generics.RetrieveUpdateAPIView):
    """Get/Update gym details"""
    serializer_class = GymSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user.gym


class DashboardStatsView(APIView):
    """Dashboard statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from members.models import Member
        from payments.models import Payment
        from datetime import date, timedelta
        
        gym = request.user.gym
        today = date.today()
        
        # Get statistics
        total_members = Member.objects.filter(gym=gym).count()
        active_members = Member.objects.filter(gym=gym, status='ACTIVE').count()
        expiring_soon = Member.objects.filter(
            gym=gym, 
            status='ACTIVE',
            membership_end_date__gte=today,
            membership_end_date__lte=today + timedelta(days=7)
        ).count()
        
        # This month's income
        this_month_start = today.replace(day=1)
        this_month_income = Payment.objects.filter(
            gym=gym,
            payment_date__gte=this_month_start,
            status='PAID'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        return Response({
            'total_members': total_members,
            'active_members': active_members,
            'expiring_soon': expiring_soon,
            'this_month_income': float(this_month_income),
        })


class ActivityLogListView(generics.ListAPIView):
    """List activity logs"""
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ActivityLog.objects.filter(gym=self.request.user.gym)[:50]