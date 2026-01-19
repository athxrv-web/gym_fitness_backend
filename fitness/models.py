from django.db import models


# ==================== DIET MODELS ====================

class DietPlan(models.Model):
    """Diet plans based on user profile"""
    CATEGORY_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('non_vegetarian', 'Non-Vegetarian'),
        ('eggetarian', 'Eggetarian'),
        ('supplement', 'Supplement'),
    ]
    
    AGE_GROUP_CHOICES = [
        ('18-36', '18-36 Years'),
        ('36-60', '36-60 Years'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    height_min = models.IntegerField(help_text="Height in inches")
    height_max = models.IntegerField(help_text="Height in inches")
    weight_min = models.IntegerField(help_text="Weight in kg")
    weight_max = models.IntegerField(help_text="Weight in kg")
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    total_calories = models.IntegerField()
    total_protein = models.IntegerField(help_text="in grams")
    total_carbs = models.IntegerField(help_text="in grams")
    total_fat = models.IntegerField(help_text="in grams")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def str(self):
        return f"{self.title} - {self.category}"


class Meal(models.Model):
    """Individual meals in a diet plan"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snack', 'Snack'),
        ('dinner', 'Dinner'),
    ]
    
    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='meals')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    calories = models.IntegerField()
    protein = models.IntegerField(help_text="in grams")
    carbs = models.IntegerField(help_text="in grams")
    fat = models.IntegerField(help_text="in grams")
    
    def str(self):
        return f"{self.diet_plan.title} - {self.meal_type}: {self.name}"


class Supplement(models.Model):
    """Supplement information"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    benefits = models.TextField()
    
    def str(self):
        return self.name


class BodyPart(models.Model):
    """Body parts for workouts"""
    BODY_PART_CHOICES = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('biceps', 'Biceps'),
        ('triceps', 'Triceps'),
        ('shoulders', 'Shoulders'),
        ('legs', 'Legs'),
    ]
    
    name = models.CharField(max_length=20, choices=BODY_PART_CHOICES, unique=True)
    description = models.TextField(blank=True)
    
    def str(self):
        return self.get_name_display()


class Exercise(models.Model):
    """Exercises for each body part"""
    body_part = models.ForeignKey(BodyPart, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=200)
    target_zone = models.CharField(max_length=100, help_text="e.g., Upper Chest, Long Head")
    description = models.TextField(blank=True)
    
    def str(self):
        return f"{self.body_part.name} - {self.target_zone}: {self.name}"


class DailyTracker(models.Model):
    """Track daily attendance, diet, and workout"""
    date = models.DateField()
    attendance = models.BooleanField(default=False, help_text="Gym attendance")
    diet_followed = models.BooleanField(default=False, help_text="Diet plan followed")
    workout_completed = models.BooleanField(default=False, help_text="Workout completed")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['date']
    
    def str(self):
        return f"Tracker - {self.date}"