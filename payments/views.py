"""
Payments Views
Optimized for PDF Generation Safety & Error Handling
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

# Ensure utils exists, otherwise handle gracefully
try:
    from .utils import generate_receipt_pdf
except ImportError:
    # Fallback to prevent crash if utils.py is missing
    def generate_receipt_pdf(receipt):
        return None

class PaymentListCreateView(generics.ListCreateAPIView):
    """List all payments or create new payment"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
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
        except Exception as e:
            return Payment.objects.none() # Return empty list on error
    
    def perform_create(self, serializer):
        try:
            payment = serializer.save(
                gym=self.request.user.gym,
                created_by=self.request.user
            )
            
            # Log activity safely
            ip = self.request.META.get('REMOTE_ADDR')
            ActivityLog.objects.create(
                user=self.request.user,
                gym=self.request.user.gym,
                action='PAYMENT_ADD',
                description=f'Payment recorded: ₹{payment.amount} from {payment.member.name}',
                ip_address=ip
            )
        except Exception as e:
            # Save ho gaya but log fail hua toh koi baat nahi
            pass


class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a payment"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(gym=self.request.user.gym)


class GenerateReceiptView(APIView):
    """Generate PDF receipt for a payment (Safe Mode)"""
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
                
                receipt = Receipt.objects.create(
                    payment=payment,
                    gym=request.user.gym,
                    member=payment.member,
                    receipt_number=receipt_number
                )
            
            # 📄 PDF Generation (Risky Process - Wrapped in Try/Except)
            try:
                pdf_file = generate_receipt_pdf(receipt)
                if pdf_file:
                    receipt.receipt_pdf = pdf_file
                    receipt.save()
                else:
                    # PDF fail hua toh bhi Data return karo
                    print("PDF Generation returned None")
            except Exception as pdf_error:
                print(f"PDF Error: {pdf_error}")
            
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
        except Exception as e:
            return Response(
                {'error': f'Failed to generate receipt: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReceiptListView(generics.ListAPIView):
    """List all receipts"""
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Receipt.objects.filter(gym=self.request.user.gym)


class PaymentStatsView(APIView):
    """Payment statistics (Zero-Safe)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            gym = request.user.gym
            today = date.today()
            
            # Helper to safely get total
            def get_stats(queryset):
                stats = queryset.aggregate(total=Sum('amount'), count=Count('id'))
                return {
                    'total': float(stats['total']) if stats['total'] else 0.0,
                    'count': stats['count'] or 0
                }

            # This month
            month_start = today.replace(day=1)
            this_month_stats = get_stats(Payment.objects.filter(
                gym=gym, payment_date__gte=month_start, status='PAID'
            ))
            
            # Today
            today_stats = get_stats(Payment.objects.filter(
                gym=gym, payment_date=today, status='PAID'
            ))
            
            # Last 7 days
            week_ago = today - timedelta(days=7)
            last_week_stats = get_stats(Payment.objects.filter(
                gym=gym, payment_date__gte=week_ago, status='PAID'
            ))
            
            return Response({
                'this_month': this_month_stats,
                'today': today_stats,
                'last_week': last_week_stats
            })
        except Exception as e:
            # Fallback agar calculation fail ho
            return Response({
                'this_month': {'total': 0.0, 'count': 0},
                'today': {'total': 0.0, 'count': 0},
                'last_week': {'total': 0.0, 'count': 0},
                'error': str(e)
            })