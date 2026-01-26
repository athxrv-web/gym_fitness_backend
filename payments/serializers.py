"""
Payments Serializers
"""
from rest_framework import serializers
from .models import Payment, Receipt
from members.serializers import MemberListSerializer


class PaymentSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True)
    member_phone = serializers.CharField(source='member.phone', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'member', 'member_name', 'member_phone', 'amount',
            'payment_method', 'payment_date', 'month', 'status',
            'transaction_id', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReceiptSerializer(serializers.ModelSerializer):
    payment_details = PaymentSerializer(source='payment', read_only=True)
    member_name = serializers.CharField(source='member.name', read_only=True)
    
    class Meta:
        model = Receipt
        fields = [
            'id', 'payment', 'payment_details', 'member', 'member_name',
            'receipt_number', 'receipt_pdf', 'sent_via_whatsapp',
            'whatsapp_sent_at', 'created_at'
        ]
        read_only_fields = ['id', 'receipt_number', 'created_at']