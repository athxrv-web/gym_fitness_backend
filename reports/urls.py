"""
Reports URLs
"""
from django.urls import path
from .views import (
    IncomeReportView, MemberReportView, MonthlyDueListView,
    ExportIncomeReportPDFView
)

app_name = 'reports'

urlpatterns = [
    path('income/', IncomeReportView.as_view(), name='income'),
    path('members/', MemberReportView.as_view(), name='members'),
    path('monthly-due/', MonthlyDueListView.as_view(), name='monthly-due'),
    path('income/export-pdf/', ExportIncomeReportPDFView.as_view(), name='income-pdf'),
]