"""
Reminders Models
"""
from django.db import models
from fitness.models import Gym, User
from members.models import Member
import uuid
from datetime import date  # ADD THIS


class Reminder(models.Model):
    """Payment Reminder Model"""
    
    TYPE_CHOICES = [
        ('PAYMENT_DUE', 'Payment Due'),
        ('MEMBERSHIP_EXPIRING', 'Membership Expiring'),
        ('RENEWAL', 'Renewal Reminder'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='reminders')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reminders')
    
    reminder_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.TextField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Delivery status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivery_status = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # ADD blank=True
    
    class Meta:
        db_table = 'reminders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['gym', 'status']),
            models.Index(fields=['member', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_reminder_type_display()} - {self.member.name}"