from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DietPlanViewSet, SupplementViewSet, BodyPartViewSet,
    ExerciseViewSet, DailyTrackerViewSet
)

router = DefaultRouter()
router.register(r'diet-plans', DietPlanViewSet, basename='dietplan')
router.register(r'supplements', SupplementViewSet, basename='supplement')
router.register(r'body-parts', BodyPartViewSet, basename='bodypart')
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'tracker', DailyTrackerViewSet, basename='tracker')

urlpatterns = [
    path('', include(router.urls)),
]