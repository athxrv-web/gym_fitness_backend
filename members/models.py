"""
Members Models
"""
from django.db import models
from fitness.models import Gym, User
import uuid
from datetime import date


class Member(models.Model):
    """Member Model"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('EXPIRED', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='members')
    
    # Personal Information
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Physical Info
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height in cm")
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kg")
    photo = models.ImageField(upload_to='member_photos/', null=True, blank=True)
    
    # Membership Details
    join_date = models.DateField(default=date.today)
    membership_type = models.CharField(max_length=50)
    membership_fee = models.DecimalField(max_digits=10, decimal_places=2)
    membership_start_date = models.DateField()
    membership_end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Health Info
    medical_conditions = models.TextField(blank=True, null=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'members'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['gym', 'status']),
            models.Index(fields=['phone']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.phone}"
    
    @property
    def days_remaining(self):
        if self.membership_end_date:
            delta = self.membership_end_date - date.today()
            return max(0, delta.days)
        return 0
    
    @property
    def is_expiring_soon(self):
        return 0 < self.days_remaining <= 7
    
    def update_status(self):
        """Update member status based on membership end date"""
        if self.membership_end_date < date.today():
            self.status = 'EXPIRED'
            self.save()


class MemberAttendance(models.Model):
    """Member Attendance/Check-in"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances')
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'member_attendances'
        ordering = ['-check_in_time']
    
    def __str__(self):
        return f"{self.member.name} - {self.check_in_time.date()}"


class MembershipPlan(models.Model):
    """Membership Plans"""
    
    DURATION_CHOICES = [
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly (3 months)'),
        ('HALF_YEARLY', 'Half Yearly (6 months)'),
        ('YEARLY', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='membership_plans')
    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    duration_days = models.IntegerField(help_text="Duration in days")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'membership_plans'
        ordering = ['duration_days']
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}"