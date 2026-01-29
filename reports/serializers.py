"""
Reports Serializers
Read-Only Serializers for Analytics & Dashboard Charts
"""
from rest_framework import serializers

class IncomeReportSerializer(serializers.Serializer):
    """
    Serializer for Financial Reports
    Used for: Income Graphs & Payment Method Pie Charts
    """
    period = serializers.CharField(read_only=True)
    total_income = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_payments = serializers.IntegerField(read_only=True)
    payment_methods = serializers.DictField(read_only=True) # Example: {'UPI': 5000, 'CASH': 2000}


class MemberReportSerializer(serializers.Serializer):
    """
    Serializer for Member Statistics
    Used for: Dashboard Counters & Gender Ratio
    """
    total_members = serializers.IntegerField(read_only=True)
    active_members = serializers.IntegerField(read_only=True)
    inactive_members = serializers.IntegerField(read_only=True)
    expired_members = serializers.IntegerField(read_only=True)
    new_this_month = serializers.IntegerField(read_only=True)
    gender_distribution = serializers.DictField(read_only=True) # Example: {'M': 50, 'F': 20}