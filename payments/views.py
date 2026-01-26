"""
Payments Views
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Sum, Count
from datetime import date, timedelta
from .models import Payment, Receipt
from .serializers import PaymentSerializer, ReceiptSerializer
from fitness.models import ActivityLog
from .utils import generate_receipt_pdf


class PaymentListCreateView(generics.ListCreateAPIView):
    """List all payments or create new payment"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Payment.objects.filter(gym=self.request.user.gym)
        
        # Filter by member
        member_id = self.request.query_params.get('member_id')
        if member_id:
            queryset = queryset.filter(member_id=member_id)
        
        # Filter by month
        month = self.request.query_params.get('month')
        if month:
            queryset = queryset.filter(month=month)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        payment = serializer.save(
            gym=self.request.user.gym,
            created_by=self.request.user
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=self.request.user,
            gym=self.request.user.gym,
            action='PAYMENT_ADD',
            description=f'Payment recorded: ₹{payment.amount} from {payment.member.name}',
            ip_address=self.request.META.get('REMOTE_ADDR')
        )


class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a payment"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(gym=self.request.user.gym)


class GenerateReceiptView(APIView):
    """Generate PDF receipt for a payment"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, gym=request.user.gym)
            
            # Check if receipt already exists
            if hasattr(payment, 'receipt'):
                receipt = payment.receipt
            else:
                # Generate receipt number
                receipt_number = Receipt.generate_receipt_number(request.user.gym)
                
                # Create receipt
                receipt = Receipt.objects.create(
                    payment=payment,
                    gym=request.user.gym,
                    member=payment.member,
                    receipt_number=receipt_number
                )
            
            # Generate PDF
            pdf_file = generate_receipt_pdf(receipt)
            receipt.receipt_pdf = pdf_file
            receipt.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                gym=request.user.gym,
                action='RECEIPT_GENERATED',
                description=f'Receipt generated: {receipt.receipt_number}'
            )
            
            serializer = ReceiptSerializer(receipt)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ReceiptListView(generics.ListAPIView):
    """List all receipts"""
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Receipt.objects.filter(gym=self.request.user.gym)


class PaymentStatsView(APIView):
    """Payment statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        gym = request.user.gym
        today = date.today()
        
        # This month
        month_start = today.replace(day=1)
        this_month = Payment.objects.filter(
            gym=gym,
            payment_date__gte=month_start,
            status='PAID'
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # Today
        today_payments = Payment.objects.filter(
            gym=gym,
            payment_date=today,
            status='PAID'
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # Last 7 days
        week_ago = today - timedelta(days=7)
        last_week = Payment.objects.filter(
            gym=gym,
            payment_date__gte=week_ago,
            status='PAID'
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        return Response({
            'this_month': {
                'total': float(this_month['total'] or 0),
                'count': this_month['count']
            },
            'today': {
                'total': float(today_payments['total'] or 0),
                'count': today_payments['count']
            },
            'last_week': {
                'total': float(last_week['total'] or 0),
                'count': last_week['count']
            }
        })