"""
Reminders URLs
"""
from django.urls import path
from .views import (
    ReminderListCreateView, ReminderDetailView, SendReminderView,
    AutoGenerateRemindersView, BulkSendRemindersView
)

app_name = 'reminders'

urlpatterns = [
    path('', ReminderListCreateView.as_view(), name='reminder-list'),
    path('<uuid:pk>/', ReminderDetailView.as_view(), name='reminder-detail'),
    path('<uuid:reminder_id>/send/', SendReminderView.as_view(), name='send'),
    path('auto-generate/', AutoGenerateRemindersView.as_view(), name='auto-generate'),
    path('bulk-send/', BulkSendRemindersView.as_view(), name='bulk-send'),
]