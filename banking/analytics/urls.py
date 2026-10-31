from django.urls import path
from .views import DashboardAnalyticsView, FinancialInsightsView

urlpatterns = [
    path('analytics/dashboard/', DashboardAnalyticsView.as_view(), name='analytics-dashboard'),
    path('analytics/insights/', FinancialInsightsView.as_view(), name='analytics-insights'),
]

