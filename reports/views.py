"""
Reports Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from payments.models import Payment
from members.models import Member
from .utils import generate_income_report_pdf


class IncomeReportView(APIView):
    """Generate income report"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        gym = request.user.gym
        
        # Get period (default: this_month)
        period = request.query_params.get('period', 'this_month')
        today = date.today()
        
        if period == 'today':
            start_date = today
            end_date = today
        elif period == 'this_week':
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif period == 'this_month':
            start_date = today.replace(day=1)
            end_date = today
        elif period == 'this_year':
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif period == 'custom':
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            if not start_date or not end_date:
                return Response({'error': 'start_date and end_date required for custom period'}, status=400)
        else:
            start_date = today.replace(day=1)
            end_date = today
        
        # Get payments in period
        payments = Payment.objects.filter(
            gym=gym,
            payment_date__gte=start_date,
            payment_date__lte=end_date,
            status='PAID'
        )
        
        # Calculate totals
        total_income = payments.aggregate(total=Sum('amount'))['total'] or 0
        total_payments = payments.count()
        
        # Payment method breakdown
        payment_methods = {}
        for method, label in Payment.PAYMENT_METHOD_CHOICES:
            amount = payments.filter(payment_method=method).aggregate(total=Sum('amount'))['total'] or 0
            count = payments.filter(payment_method=method).count()
            payment_methods[label] = {
                'amount': float(amount),
                'count': count
            }
        
        # Daily breakdown (for charts)
        daily_data = []
        current_date = start_date
        while current_date <= end_date:
            day_total = payments.filter(payment_date=current_date).aggregate(total=Sum('amount'))['total'] or 0
            daily_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'amount': float(day_total)
            })
            current_date += timedelta(days=1)
        
        return Response({
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'total_income': float(total_income),
            'total_payments': total_payments,
            'payment_methods': payment_methods,
            'daily_breakdown': daily_data
        })


class MemberReportView(APIView):
    """Generate member statistics report"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        gym = request.user.gym
        today = date.today()
        month_start = today.replace(day=1)
        
        # Overall stats
        total_members = Member.objects.filter(gym=gym).count()
        active_members = Member.objects.filter(gym=gym, status='ACTIVE').count()
        inactive_members = Member.objects.filter(gym=gym, status='INACTIVE').count()
        expired_members = Member.objects.filter(gym=gym, status='EXPIRED').count()
        
        # New members this month
        new_this_month = Member.objects.filter(
            gym=gym,
            created_at__gte=month_start
        ).count()
        
        # Gender distribution
        male = Member.objects.filter(gym=gym, gender='M').count()
        female = Member.objects.filter(gym=gym, gender='F').count()
        other = Member.objects.filter(gym=gym, gender='O').count()
        
        # Expiring soon (next 7 days)
        expiry_date = today + timedelta(days=7)
        expiring_soon = Member.objects.filter(
            gym=gym,
            status='ACTIVE',
            membership_end_date__gte=today,
            membership_end_date__lte=expiry_date
        ).count()
        
        # Membership type distribution
        membership_types = Member.objects.filter(gym=gym).values('membership_type').annotate(
            count=Count('id')
        )
        
        return Response({
            'total_members': total_members,
            'active_members': active_members,
            'inactive_members': inactive_members,
            'expired_members': expired_members,
            'new_this_month': new_this_month,
            'expiring_soon': expiring_soon,
            'gender_distribution': {
                'male': male,
                'female': female,
                'other': other
            },
            'membership_types': list(membership_types)
        })


class MonthlyDueListView(APIView):
    """List of members with pending payments"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from members.serializers import MemberListSerializer
        
        gym = request.user.gym
        today = date.today()
        current_month = today.strftime('%B %Y')
        
        # Get all active members
        active_members = Member.objects.filter(gym=gym, status='ACTIVE')
        
        due_members = []
        for member in active_members:
            # Check if payment exists for current month
            has_paid = Payment.objects.filter(
                gym=gym,
                member=member,
                month=current_month,
                status='PAID'
            ).exists()
            
            if not has_paid:
                due_members.append({
                    'member': MemberListSerializer(member).data,
                    'amount_due': float(member.membership_fee),
                    'month': current_month
                })
        
        return Response({
            'month': current_month,
            'total_due': len(due_members),
            'members': due_members
        })


class ExportIncomeReportPDFView(APIView):
    """Export income report as PDF"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.http import FileResponse
        
        gym = request.user.gym
        period = request.query_params.get('period', 'this_month')
        
        # Generate PDF
        pdf_file = generate_income_report_pdf(gym, period)
        
        return FileResponse(
            pdf_file,
            as_attachment=True,
            filename=f'income_report_{period}.pdf'
        )