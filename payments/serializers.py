"""
Payments Serializers
Optimized for Data Integrity & Frontend Compatibility
"""
from rest_framework import serializers
from .models import Payment, Receipt
# Note: MemberListSerializer import rakha hai agar future me nested use karna ho
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

    # 🛡️ SECURITY FIX: Amount Validation
    def validate_amount(self, value):
        """Ensure payment is positive"""
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero.")
        return value

    # 🛡️ CRASH PROOFING: Handle Empty Strings
    def to_internal_value(self, data):
        """
        Clean data before validation.
        Converts empty 'amount' strings to None to avoid Server Error 500.
        """
        if hasattr(data, '_mutable'):
            data._mutable = True
            
        # Agar amount khali hai, toh None bana do (Required validator isse pakad lega)
        if 'amount' in data and data['amount'] == "":
            data['amount'] = None
            
        return super().to_internal_value(data)


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