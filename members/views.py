"""
Members Views - FINAL PRO VERSION
✅ Supports: Admin Login, Member Phone Login
✅ Features: Camera Upload, Auto-Stats, Error Handling
"""
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny # ✅ AllowAny zaroori hai
from rest_framework.decorators import api_view, permission_classes # ✅ Decorators zaroori hain
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser 
from django.db import IntegrityError 
from django.db.models import Q
from datetime import date, timedelta

from .models import Member, MemberAttendance, MembershipPlan
from .serializers import (
    MemberSerializer, MemberListSerializer, 
    MemberAttendanceSerializer, MembershipPlanSerializer
)
from fitness.models import ActivityLog

# ==========================================
# 1. MEMBER MANAGEMENT (ADMIN ONLY)
# ==========================================

class MemberListCreateView(generics.ListCreateAPIView):
    """
    List all members or Create new member
    ✅ Supports Multipart (Photo Upload from Camera/Gallery)
    """
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser) # 📸 Zaroori line
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone', 'email']
    ordering_fields = ['name', 'created_at', 'membership_end_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MemberListSerializer
        return MemberSerializer
    
    def get_queryset(self):
        # Sirf iss gym ke members dikhao
        queryset = Member.objects.filter(gym=self.request.user.gym)
        
        status_param = self.request.query_params.get('status', None)
        if status_param == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_param == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        gender = self.request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender=gender)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"error": "A member with this Phone Number already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_create(self, serializer):
        member = serializer.save(gym=self.request.user.gym)
        # Log Activity
        ActivityLog.objects.create(
            user=self.request.user,
            gym=self.request.user.gym,
            action='MEMBER_ADD',
            description=f'Added new member: {member.name}',
            ip_address=self.request.META.get('REMOTE_ADDR')
        )

class MemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a member"""
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        return Member.objects.filter(gym=self.request.user.gym)
    
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"error": "Number already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_update(self, serializer):
        member = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            gym=self.request.user.gym,
            action='MEMBER_UPDATE',
            description=f'Updated member: {member.name}',
            ip_address=self.request.META.get('REMOTE_ADDR')
        )

# ==========================================
# 2. ATTENDANCE & STATS (ADMIN ONLY)
# ==========================================

class MemberCheckInView(APIView):
    """Record member check-in"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            member = Member.objects.get(pk=pk, gym=request.user.gym)
            attendance = MemberAttendance.objects.create(
                member=member,
                gym=request.user.gym,
                notes=request.data.get('notes', '')
            )
            serializer = MemberAttendanceSerializer(attendance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Member.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)

class MemberAttendanceListView(generics.ListAPIView):
    serializer_class = MemberAttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = MemberAttendance.objects.filter(gym=self.request.user.gym)
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        member_id = self.request.query_params.get('member_id')

        if start_date: queryset = queryset.filter(check_in_time__date__gte=start_date)
        if end_date: queryset = queryset.filter(check_in_time__date__lte=end_date)
        if member_id: queryset = queryset.filter(member_id=member_id)
        
        return queryset.order_by('-check_in_time')

class ExpiringMembersView(generics.ListAPIView):
    serializer_class = MemberListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        today = date.today()
        expiry_date = today + timedelta(days=7)
        return Member.objects.filter(
            gym=self.request.user.gym,
            is_active=True, 
            membership_end_date__gte=today,
            membership_end_date__lte=expiry_date
        ).order_by('membership_end_date')

class ExpiredMembersView(generics.ListAPIView):
    serializer_class = MemberListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        today = date.today()
        return Member.objects.filter(
            gym=self.request.user.gym,
            membership_end_date__lt=today
        ).order_by('-membership_end_date')

class MemberStatsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        gym = request.user.gym
        today = date.today()
        
        total = Member.objects.filter(gym=gym).count()
        active = Member.objects.filter(gym=gym, is_active=True).count()
        inactive = Member.objects.filter(gym=gym, is_active=False).count()
        expired = Member.objects.filter(gym=gym, membership_end_date__lt=today).count()
        
        male = Member.objects.filter(gym=gym, gender='M').count()
        female = Member.objects.filter(gym=gym, gender='F').count()
        other = Member.objects.filter(gym=gym, gender='O').count()
        
        return Response({
            'total': total, 'active': active, 'inactive': inactive, 'expired': expired,
            'gender_distribution': {'male': male, 'female': female, 'other': other}
        })

# ==========================================
# 3. MEMBERSHIP PLANS (ADMIN ONLY)
# ==========================================

class MembershipPlanListCreateView(generics.ListCreateAPIView):
    serializer_class = MembershipPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MembershipPlan.objects.filter(gym=self.request.user.gym, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(gym=self.request.user.gym)

class MembershipPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MembershipPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MembershipPlan.objects.filter(gym=self.request.user.gym)

# ==========================================
# 4. MEMBER APP LOGIN (PUBLIC ACCESS)
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny]) # ✅ BINA TOKEN KE CHALEGA
def check_member_status(request):
    """
    Check member status by phone number.
    Used for Member App Login without password.
    """
    phone = request.data.get('phone')
    
    if not phone:
        return Response({'detail': 'Phone number is required'}, status=400)
    
    try:
        # Phone se search karo
        member = Member.objects.filter(phone=phone).first()
        
        if member:
            # Pura data bhejo dashboard ke liye
            serializer = MemberSerializer(member)
            return Response(serializer.data, status=200)
        else:
            return Response({'detail': 'Member not found'}, status=404)
            
    except Exception as e:
        return Response({'detail': str(e)}, status=500)