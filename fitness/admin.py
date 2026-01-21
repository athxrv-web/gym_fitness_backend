from django.contrib import admin
from .models import (
    BodyPart, Exercise, DietPlan, Meal, Supplement,
    DailyTracker, UserProfile
)

@admin.register(BodyPart)
class BodyPartAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'body_part', 'target_area')
    list_filter = ('body_part',)
    search_fields = ('name', 'target_area')

@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    # 'title' ki jagah ab 'name' hai
    list_display = ('name', 'gender', 'age_group', 'category') 
    list_filter = ('gender', 'category')

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'diet_plan', 'time', 'calories')
    list_filter = ('diet_plan', 'time')

@admin.register(Supplement)
class SupplementAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(DailyTracker)
class DailyTrackerAdmin(admin.ModelAdmin):
    # Purane fields hata diye, naye add kar diye
    list_display = ('user', 'date', 'calories_consumed', 'workout_done') 
    list_filter = ('date', 'workout_done')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'fees_status', 'expiry_date')
    list_filter = ('user_type', 'fees_status', 'time_slot')
    search_fields = ('user__username', 'mobile_number')
    # fitness/admin.py (Add at the bottom)
from django.utils.html import format_html
from datetime import date
from .models import IOSMember # <--- Import zaroor karna

@admin.register(IOSMember)
class IOSMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile_number', 'fees_status', 'days_left_status')
    list_filter = ('fees_status', 'time_slot')
    search_fields = ('name', 'mobile_number')

    # --- CRAZY REMINDER LOGIC ---
    def days_left_status(self, obj):
        today = date.today()
        if obj.expiry_date:
            days_left = (obj.expiry_date - today).days
            
            if days_left <= 0:
                # Expired (Red Color)
                return format_html(
                    '<span style="color: red; font-weight: bold;">⚠️ DUE (Expired {} days ago)</span>', 
                    abs(days_left)
                )
            elif days_left <= 5:
                # Warning (Orange Color)
                return format_html(
                    '<span style="color: orange; font-weight: bold;">⚠️ Due in {} days</span>', 
                    days_left
                )
            else:
                # Safe (Green Color)
                return format_html(
                    '<span style="color: green;">✅ Active ({} days left)</span>', 
                    days_left
                )
        return "No Date Set"
    
    days_left_status.short_description = "Fees Reminder"