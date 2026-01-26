"""
Reminders Views
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from datetime import date, timedelta
from .models import Reminder
from .serializers import ReminderSerializer
from members.models import Member
from whatsapp.services import WhatsAppService


class ReminderListCreateView(generics.ListCreateAPIView):
    """List all reminders or create new reminder"""
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Reminder.objects.filter(gym=self.request.user.gym)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by member
        member_id = self.request.query_params.get('member_id')
        if member_id:
            queryset = queryset.filter(member_id=member_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(
            gym=self.request.user.gym,
            created_by=self.request.user
        )


class ReminderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a reminder"""
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Reminder.objects.filter(gym=self.request.user.gym)


class SendReminderView(APIView):
    """Send a reminder via WhatsApp"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, reminder_id):
        try:
            reminder = Reminder.objects.get(id=reminder_id, gym=request.user.gym)
            
            # Check if WhatsApp is enabled
            if not request.user.gym.whatsapp_enabled:
                return Response(
                    {'error': 'WhatsApp notifications are disabled for your gym'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Send WhatsApp message
            whatsapp_service = WhatsAppService()
            result = whatsapp_service.send_reminder(reminder)
            
            if result['success']:
                reminder.status = 'SENT'
                reminder.sent_at = date.today()
                reminder.delivery_status = 'Delivered'
            else:
                reminder.status = 'FAILED'
                reminder.error_message = result.get('error', 'Unknown error')
            
            reminder.save()
            
            serializer = ReminderSerializer(reminder)
            return Response(serializer.data)
        
        except Reminder.DoesNotExist:
            return Response(
                {'error': 'Reminder not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class AutoGenerateRemindersView(APIView):
    """Auto-generate reminders for expiring memberships"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        gym = request.user.gym
        today = date.today()
        reminder_date = today + timedelta(days=7)
        
        # Find members expiring in 7 days
        expiring_members = Member.objects.filter(
            gym=gym,
            status='ACTIVE',
            membership_end_date__gte=today,
            membership_end_date__lte=reminder_date
        )
        
        created_count = 0
        
        for member in expiring_members:
            # Check if reminder already exists
            existing = Reminder.objects.filter(
                gym=gym,
                member=member,
                reminder_type='MEMBERSHIP_EXPIRING',
                due_date=member.membership_end_date,
                status__in=['PENDING', 'SENT']
            ).exists()
            
            if not existing:
                days_left = (member.membership_end_date - today).days
                
                message = f"""
Dear {member.name},

Your gym membership at {gym.name} is expiring in {days_left} days on {member.membership_end_date.strftime('%d-%b-%Y')}.

Please renew your membership to continue enjoying our services.

Membership Fee: ₹{member.membership_fee}

Contact us: {gym.phone}

Thank you!
{gym.name}
                """.strip()
                
                Reminder.objects.create(
                    gym=gym,
                    member=member,
                    reminder_type='MEMBERSHIP_EXPIRING',
                    message=message,
                    due_date=member.membership_end_date,
                    amount=member.membership_fee,
                    created_by=request.user
                )
                created_count += 1
        
        return Response({
            'message': f'Created {created_count} reminders',
            'count': created_count
        })


class BulkSendRemindersView(APIView):
    """Send all pending reminders"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        gym = request.user.gym
        
        if not gym.whatsapp_enabled:
            return Response(
                {'error': 'WhatsApp notifications are disabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get pending reminders
        pending_reminders = Reminder.objects.filter(
            gym=gym,
            status='PENDING'
        )
        
        whatsapp_service = WhatsAppService()
        sent_count = 0
        failed_count = 0
        
        for reminder in pending_reminders:
            result = whatsapp_service.send_reminder(reminder)
            
            if result['success']:
                reminder.status = 'SENT'
                reminder.sent_at = date.today()
                reminder.delivery_status = 'Delivered'
                sent_count += 1
            else:
                reminder.status = 'FAILED'
                reminder.error_message = result.get('error', 'Unknown error')
                failed_count += 1
            
            reminder.save()
        
        return Response({
            'message': f'Sent {sent_count} reminders, {failed_count} failed',
            'sent': sent_count,
            'failed': failed_count
        })