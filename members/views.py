"""
Members Views
Optimized for Flutter Multipart Uploads & Error Handling
"""
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser # 📸 Zaroori hai Photo ke liye
from django.db import IntegrityError # 🛡️ Duplicate pakadne ke liye
from django.db.models import Q
from datetime import date, timedelta

from .models import Member, MemberAttendance, MembershipPlan
from .serializers import (
    MemberSerializer, MemberListSerializer, 
    MemberAttendanceSerializer, MembershipPlanSerializer
)
from fitness.models import ActivityLog


class MemberListCreateView(generics.ListCreateAPIView):
    """
    List all members or Create new member
    ✅ Supports Multipart (Photo Upload)
    ✅ Handles Duplicate Phone Numbers gracefully
    """
    permission_classes = [IsAuthenticated]
    # 📸 Parsers add kiye taaki Flutter se Photo accept ho sake
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone', 'email']
    ordering_fields = ['name', 'created_at', 'membership_end_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        # List ke liye halka serializer, Create ke liye heavy wala
        if self.request.method == 'GET':
            return MemberListSerializer
        return MemberSerializer
    
    def get_queryset(self):
        queryset = Member.objects.filter(gym=self.request.user.gym)
        
        # Filter by Active Status (Boolean Fix)
        status_param = self.request.query_params.get('status', None)
        if status_param == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_param == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Filter by gender
        gender = self.request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender=gender)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Overriding create to handle Errors (500 -> 400)
        """
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            # 🛡️ Agar Phone Number duplicate hai, toh ye error aayega
            return Response(
                {"error": "A member with this Phone Number already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Koi aur error ho toh Server Crash mat hone do
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_create(self, serializer):
        # Gym aur Created By apne aap set hoga
        member = serializer.save(
            gym=self.request.user.gym
            # created_by field agar model me hai toh add karein, warna hata dein
        )
        
        # Log activity
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
    # Update karte waqt bhi photo upload ho sakti hai
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        return Member.objects.filter(gym=self.request.user.gym)
    
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"error": "This Phone Number is already taken by another member."},
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
            return Response(
                {'error': 'Member not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MemberAttendanceListView(generics.ListAPIView):
    """List attendance records"""
    serializer_class = MemberAttendanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = MemberAttendance.objects.filter(gym=self.request.user.gym)
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        member_id = self.request.query_params.get('member_id')

        if start_date:
            queryset = queryset.filter(check_in_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(check_in_time__date__lte=end_date)
        if member_id:
            queryset = queryset.filter(member_id=member_id)
        
        return queryset.order_by('-check_in_time')


class ExpiringMembersView(generics.ListAPIView):
    """List members expiring in next 7 days"""
    serializer_class = MemberListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        today = date.today()
        expiry_date = today + timedelta(days=7)
        
        return Member.objects.filter(
            gym=self.request.user.gym,
            is_active=True, # ✅ Fixed: Using Boolean Field
            membership_end_date__gte=today,
            membership_end_date__lte=expiry_date
        ).order_by('membership_end_date')


class ExpiredMembersView(generics.ListAPIView):
    """List expired members"""
    serializer_class = MemberListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        today = date.today()
        return Member.objects.filter(
            gym=self.request.user.gym,
            membership_end_date__lt=today
        ).order_by('-membership_end_date')


class MembershipPlanListCreateView(generics.ListCreateAPIView):
    """List or create membership plans"""
    serializer_class = MembershipPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MembershipPlan.objects.filter(
            gym=self.request.user.gym, 
            is_active=True
        )
    
    def perform_create(self, serializer):
        serializer.save(gym=self.request.user.gym)


class MembershipPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete membership plan"""
    serializer_class = MembershipPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MembershipPlan.objects.filter(gym=self.request.user.gym)


class MemberStatsView(APIView):
    """Member statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        gym = request.user.gym
        today = date.today()
        
        total = Member.objects.filter(gym=gym).count()
        active = Member.objects.filter(gym=gym, is_active=True).count()
        inactive = Member.objects.filter(gym=gym, is_active=False).count()
        # Expired logic: Active but date passed
        expired = Member.objects.filter(gym=gym, membership_end_date__lt=today).count()
        
        male = Member.objects.filter(gym=gym, gender='M').count()
        female = Member.objects.filter(gym=gym, gender='F').count()
        other = Member.objects.filter(gym=gym, gender='O').count()
        
        return Response({
            'total': total,
            'active': active,
            'inactive': inactive,
            'expired': expired,
            'gender_distribution': {
                'male': male,
                'female': female,
                'other': other
            }
        })