from django.contrib import admin
from .models import DietPlan, Meal, Supplement, BodyPart, Exercise, DailyTracker


class MealInline(admin.TabularInline):
    model = Meal
    extra = 1


@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'age_group', 'gender', 'total_calories']
    list_filter = ['category', 'age_group', 'gender']
    search_fields = ['title', 'description']
    inlines = [MealInline]


@admin.register(Supplement)
class SupplementAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 1


@admin.register(BodyPart)
class BodyPartAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [ExerciseInline]


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'body_part', 'target_zone']
    list_filter = ['body_part', 'target_zone']
    search_fields = ['name', 'target_zone']


@admin.register(DailyTracker)
class DailyTrackerAdmin(admin.ModelAdmin):
    list_display = ['date', 'attendance', 'diet_followed', 'workout_completed']
    list_filter = ['date', 'attendance', 'diet_followed', 'workout_completed']
    date_hierarchy = 'date'