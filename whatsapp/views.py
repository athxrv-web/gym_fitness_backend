"""
WhatsApp Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .services import WhatsAppService
from payments.models import Receipt
from fitness.models import ActivityLog


class SendReceiptWhatsAppView(APIView):
    """Send receipt via WhatsApp"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, receipt_id):
        try:
            receipt = Receipt.objects.get(id=receipt_id, gym=request.user.gym)
            
            # Check if WhatsApp is enabled
            if not request.user.gym.whatsapp_enabled:
                return Response(
                    {'error': 'WhatsApp is disabled for your gym'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Send via WhatsApp
            whatsapp_service = WhatsAppService()
            result = whatsapp_service.send_receipt(receipt)
            
            if result['success']:
                receipt.sent_via_whatsapp = True
                from django.utils import timezone
                receipt.whatsapp_sent_at = timezone.now()
                receipt.save()
                
                # Log activity
                ActivityLog.objects.create(
                    user=request.user,
                    gym=request.user.gym,
                    action='RECEIPT_SENT',
                    description=f'Receipt {receipt.receipt_number} sent via WhatsApp to {receipt.member.name}'
                )
                
                return Response({
                    'success': True,
                    'message': 'Receipt sent successfully via WhatsApp'
                })
            else:
                return Response(
                    {'success': False, 'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except Receipt.DoesNotExist:
            return Response(
                {'error': 'Receipt not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class TestWhatsAppView(APIView):
    """Test WhatsApp configuration"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        phone = request.data.get('phone')
        
        if not phone:
            return Response(
                {'error': 'Phone number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message = f"""
🏋️ Test Message from {request.user.gym.name}

This is a test message to verify WhatsApp integration.

If you received this, WhatsApp is configured correctly! ✅
        """.strip()
        
        whatsapp_service = WhatsAppService()
        result = whatsapp_service.send_message(phone, message)
        
        if result['success']:
            return Response({
                'success': True,
                'message': 'Test message sent successfully'
            })
        else:
            return Response(
                {'success': False, 'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )