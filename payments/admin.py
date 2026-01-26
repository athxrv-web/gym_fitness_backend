"""
Payments Admin
"""
from django.contrib import admin
from .models import Payment, Receipt


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount', 'payment_method', 'payment_date', 'status']
    list_filter = ['status', 'payment_method', 'payment_date', 'gym']
    search_fields = ['member__name', 'member__phone', 'transaction_id']
    date_hierarchy = 'payment_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'member', 'sent_via_whatsapp', 'created_at']
    list_filter = ['sent_via_whatsapp', 'gym', 'created_at']
    search_fields = ['receipt_number', 'member__name']
    date_hierarchy = 'created_at'