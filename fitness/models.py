from django.db import models
from django.contrib.auth.models import User
from datetime import date , timedelta

# ============================
# 1. WORKOUT MODELS
# ============================

class BodyPart(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='body_parts/', blank=True, null=True)

    def __str__(self):
        return self.name

class Exercise(models.Model):
    body_part = models.ForeignKey(BodyPart, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=100)
    
    # --- NEW FIELDS (For Tutorial Screen) ---
    target_area = models.CharField(max_length=100, blank=True, null=True, help_text="Eg: Upper Chest, Long Head")
    video_link = models.URLField(max_length=500, blank=True, null=True, help_text="YouTube/Insta Link")
    instructions = models.TextField(blank=True, null=True)
    
    image = models.ImageField(upload_to='exercises/', blank=True, null=True)

    def __str__(self):
        return self.name

# ============================
# 2. DIET MODELS
# ============================

class DietPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    age_group = models.CharField(max_length=20, choices=[('18-36', '18-36'), ('36-60', '36-60')])
    category = models.CharField(max_length=50, choices=[('Weight Loss', 'Weight Loss'), ('Muscle Gain', 'Muscle Gain')])
    image = models.ImageField(upload_to='diet_plans/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.gender})"

class Meal(models.Model):
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='meals')
    name = models.CharField(max_length=100)
    time = models.CharField(max_length=50) # Breakfast, Lunch, etc.
    calories = models.IntegerField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fats = models.FloatField()
    description = models.TextField()

    def __str__(self):
        return self.name

class Supplement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    usage = models.TextField()
    image = models.ImageField(upload_to='supplements/', blank=True, null=True)

    def __str__(self):
        return self.name

# ============================
# 3. TRACKER & USER
# ============================

class DailyTracker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    calories_consumed = models.IntegerField(default=0)
    water_intake = models.FloatField(default=0.0) # In Liters
    workout_done = models.BooleanField(default=False)
    sleep_hours = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class UserProfile(models.Model):
    SLOT_CHOICES = [('Morning', 'Morning'), ('Evening', 'Evening')]
    STATUS_CHOICES = [('Paid', 'Paid'), ('Due', 'Due')]
    TYPE_CHOICES = [('Gym User', 'Gym User'), ('Non-User', 'Non-User')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Gym User')
    time_slot = models.CharField(max_length=10, choices=SLOT_CHOICES, default='Morning')
    fees_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Due')
    fees_paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fees_paid_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.fees_status}"
    # fitness/models.py (Add at the bottom)

from datetime import timedelta # <--- Upar check karna ye import hai ya nahi, nahi to add karna

class IOSMember(models.Model):
    SLOT_CHOICES = [('Morning', 'Morning'), ('Evening', 'Evening')]
    STATUS_CHOICES = [('Paid', 'Paid'), ('Unpaid', 'Unpaid')]

    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    time_slot = models.CharField(max_length=10, choices=SLOT_CHOICES, default='Morning')
    
    # Fees Info
    fees_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Dates
    joining_date = models.DateField(auto_now_add=True) # Jis din entry hui
    expiry_date = models.DateField(blank=True, null=True) # 30 din baad

    def save(self, *args, **kwargs):
        # Crazy Logic: Agar expiry date nahi dali, toh khud 30 din jod lo
        if not self.expiry_date:
            self.joining_date = date.today()
            self.expiry_date = self.joining_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (iOS)"