"""
Reports Serializers
"""
from rest_framework import serializers


class IncomeReportSerializer(serializers.Serializer):
    """Income Report Serializer"""
    period = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_payments = serializers.IntegerField()
    payment_methods = serializers.DictField()


class MemberReportSerializer(serializers.Serializer):
    """Member Report Serializer"""
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    inactive_members = serializers.IntegerField()
    expired_members = serializers.IntegerField()
    new_this_month = serializers.IntegerField()
    gender_distribution = serializers.DictField()