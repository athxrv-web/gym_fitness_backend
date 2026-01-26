"""
Members Views
"""
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q
from datetime import date, timedelta
from .models import Member, MemberAttendance, MembershipPlan
from .serializers import (
    MemberSerializer, MemberListSerializer, 
    MemberAttendanceSerializer, MembershipPlanSerializer
)
from fitness.models import ActivityLog


class MemberListCreateView(generics.ListCreateAPIView):
    """List all members or create new member"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone', 'email']
    ordering_fields = ['name', 'created_at', 'membership_end_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MemberListSerializer
        return MemberSerializer
    
    def get_queryset(self):
        queryset = Member.objects.filter(gym=self.request.user.gym)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by gender
        gender = self.request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender=gender)
        
        return queryset
    
    def perform_create(self, serializer):
        member = serializer.save(
            gym=self.request.user.gym,
            created_by=self.request.user
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
    
    def get_queryset(self):
        return Member.objects.filter(gym=self.request.user.gym)
    
    def perform_update(self, serializer):
        member = serializer.save()
        
        # Log activity
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
            
            # Create attendance record
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
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(check_in_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(check_in_time__date__lte=end_date)
        
        # Filter by member
        member_id = self.request.query_params.get('member_id')
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
            status='ACTIVE',
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
        
        total = Member.objects.filter(gym=gym).count()
        active = Member.objects.filter(gym=gym, status='ACTIVE').count()
        inactive = Member.objects.filter(gym=gym, status='INACTIVE').count()
        expired = Member.objects.filter(gym=gym, status='EXPIRED').count()
        
        # Gender distribution
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