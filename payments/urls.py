"""
Payments URLs
"""
from django.urls import path
from .views import (
    PaymentListCreateView, PaymentDetailView, GenerateReceiptView,
    ReceiptListView, PaymentStatsView
)

app_name = 'payments'

urlpatterns = [
    # Payments
    path('', PaymentListCreateView.as_view(), name='payment-list'),
    path('<uuid:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('<uuid:payment_id>/generate-receipt/', GenerateReceiptView.as_view(), name='generate-receipt'),
    path('stats/', PaymentStatsView.as_view(), name='stats'),
    
    # Receipts
    path('receipts/', ReceiptListView.as_view(), name='receipt-list'),
]