"""
Members Models
Contains Member, MembershipPlan, and Attendance logic.
"""
from django.db import models
from fitness.models import Gym
import uuid

class MembershipPlan(models.Model):
    DURATION_CHOICES = [
        ('MONTHLY', '1 Month'), ('QUARTERLY', '3 Months'),
        ('HALFYEARLY', '6 Months'), ('YEARLY', '1 Year'), ('CUSTOM', 'Custom'),
    ]
    id = models.AutoField(primary_key=True)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='plans')
    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='MONTHLY')
    duration_days = models.IntegerField(default=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'membership_plans'

    def __str__(self):
        return f"{self.name} - ₹{self.price}"

class Member(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    MEMBERSHIP_TYPE_CHOICES = [('MONTHLY', 'Monthly'), ('QUARTERLY', 'Quarterly'), ('HALFYEARLY', 'Half Yearly'), ('YEARLY', 'Yearly')]

    id = models.AutoField(primary_key=True)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, db_index=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    age = models.IntegerField(null=True, blank=True) 
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='member_photos/', null=True, blank=True)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPE_CHOICES, default='MONTHLY')
    membership_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    join_date = models.DateField()
    membership_start_date = models.DateField()
    membership_end_date = models.DateField()
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'members'
        ordering = ['-created_at']
        unique_together = [['gym', 'phone']]

    def __str__(self):
        return f"{self.name} ({self.phone})"

class MemberAttendance(models.Model):
    id = models.AutoField(primary_key=True)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendance')
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'member_attendance'
        ordering = ['-check_in_time']

    def __str__(self):
        return f"{self.member.name} - {self.check_in_time}"