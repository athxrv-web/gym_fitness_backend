"""
WhatsApp URLs
"""
from django.urls import path
from .views import SendReceiptWhatsAppView, TestWhatsAppView

app_name = 'whatsapp'

urlpatterns = [
    path('send-receipt/<uuid:receipt_id>/', SendReceiptWhatsAppView.as_view(), name='send-receipt'),
    path('test/', TestWhatsAppView.as_view(), name='test'),
]