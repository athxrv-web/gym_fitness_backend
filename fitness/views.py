"""
Fitness Views - Authentication & Dashboard
Optimized for Security (Token Blacklist) & Stability
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum # ✅ Fix: Missing Import added
from django.utils import timezone # ✅ Fix: Better Date handling

from .models import User, Gym, ActivityLog
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, 
    GymSerializer, ActivityLogSerializer
)

# 🛠️ HELPER: Get Real IP Address (Render/Cloudflare ke peeche bhi kaam karega)
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class RegisterView(generics.CreateAPIView):
    """Register new gym owner"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # Generate JWT tokens immediately
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login with Activity Logging"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            # ✅ Log activity with Real IP
            if user.gym:
                ActivityLog.objects.create(
                    user=user,
                    gym=user.gym,
                    action='LOGIN',
                    description=f'User {user.email} logged in',
                    ip_address=get_client_ip(request)
                )
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful'
            })
        except Exception as e:
             return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """Secure User Logout (Blacklists Token)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # 🛡️ SECURITY: Blacklist the refresh token so it can't be reused
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            if request.user.gym:
                ActivityLog.objects.create(
                    user=request.user,
                    gym=request.user.gym,
                    action='LOGOUT',
                    description=f'User {request.user.email} logged out'
                )
            return Response({'message': 'Logout successful'})
        except Exception as e:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)


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
    """Dashboard statistics - CRASH PROOF"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Import models dynamically to avoid Circular Import errors
            from members.models import Member
            from payments.models import Payment
            from datetime import date, timedelta
            
            gym = request.user.gym
            today = date.today()
            
            # Get statistics
            total_members = Member.objects.filter(gym=gym).count()
            active_members = Member.objects.filter(gym=gym, is_active=True).count() # Check is_active bool
            
            # Expiring in next 7 days
            expiring_soon = Member.objects.filter(
                gym=gym, 
                is_active=True,
                membership_end_date__gte=today,
                membership_end_date__lte=today + timedelta(days=7)
            ).count()
            
            # This month's income
            this_month_start = today.replace(day=1)
            
            # ✅ Fix: Handle None result if no payments exist
            income_agg = Payment.objects.filter(
                member__gym=gym, # Link via Member -> Gym
                payment_date__gte=this_month_start,
                status='PAID'
            ).aggregate(total=Sum('amount'))
            
            this_month_income = income_agg['total'] if income_agg['total'] else 0
            
            return Response({
                'total_members': total_members,
                'active_members': active_members,
                'expiring_soon': expiring_soon,
                'this_month_income': float(this_month_income),
            })
        except Exception as e:
            print(f"Dashboard Error: {e}") # Render logs me dikhega
            return Response({
                'total_members': 0,
                'active_members': 0,
                'expiring_soon': 0,
                'this_month_income': 0.0,
                'error': 'Failed to load stats'
            }, status=status.HTTP_200_OK) # 200 return karo taaki App crash na ho


class ActivityLogListView(generics.ListAPIView):
    """List activity logs"""
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Return latest 50 logs
        return ActivityLog.objects.filter(gym=self.request.user.gym).order_by('-created_at')[:50]