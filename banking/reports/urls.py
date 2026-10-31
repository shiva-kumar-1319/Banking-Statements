from django.urls import path
from .views import TransactionCSVExportView, FinancialSummaryPDFExportView, SummaryReportView

urlpatterns = [
    path('reports/transactions/csv/', TransactionCSVExportView.as_view(), name='report-transactions-csv'),
    path('reports/financial-summary/pdf/', FinancialSummaryPDFExportView.as_view(), name='report-summary-pdf'),
    path('reports/summary/', SummaryReportView.as_view(), name='report-summary-json'),
]

