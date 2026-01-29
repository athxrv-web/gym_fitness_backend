"""
Payments Models
Optimized for Data Safety & Receipt Generation
"""
from django.db import models
from fitness.models import Gym, User
from members.models import Member
import uuid
from datetime import date

class Payment(models.Model):
    """Payment Model"""
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
        ('CARD', 'Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='payments')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    
    # 🛡️ Safety: Default 0.00 to prevent crash on empty values
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    payment_date = models.DateField(default=date.today)
    
    # Monthly tracking (Optional to prevent crash)
    month = models.CharField(max_length=20, help_text="e.g., 'January 2025'", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PAID')
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['gym', '-payment_date']),
            models.Index(fields=['member', '-payment_date']),
        ]
    
    def __str__(self):
        return f"{self.member.name} - ₹{self.amount} - {self.payment_date}"


class Receipt(models.Model):
    """Receipt Model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    
    receipt_number = models.CharField(max_length=50, unique=True, db_index=True)
    receipt_pdf = models.FileField(upload_to='receipts/', null=True, blank=True)
    
    # WhatsApp delivery
    sent_via_whatsapp = models.BooleanField(default=False)
    whatsapp_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'receipts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Receipt #{self.receipt_number}"
    
    @staticmethod
    def generate_receipt_number(gym):
        """Generate unique receipt number"""
        from datetime import datetime
        today = datetime.now()
        # Use first 8 chars of UUID to keep it short but unique per gym
        prefix = f"REC-{gym.id.hex[:8].upper()}-{today.strftime('%Y%m%d')}"
        
        # Get last receipt for today
        last_receipt = Receipt.objects.filter(
            gym=gym,
            receipt_number__startswith=prefix
        ).order_by('-created_at').first()
        
        if last_receipt:
            # Extract sequence number and increment
            try:
                last_seq = int(last_receipt.receipt_number.split('-')[-1])
                new_seq = last_seq + 1
            except ValueError:
                new_seq = 1
        else:
            new_seq = 1
        
        return f"{prefix}-{new_seq:04d}"