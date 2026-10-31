from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .report_generator import generate_csv_report, generate_pdf_report
from analytics.analytics_service import get_dashboard_data


class TransactionCSVExportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return generate_csv_report(request.user, request.query_params)


class FinancialSummaryPDFExportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return generate_pdf_report(request.user, request.query_params)


class SummaryReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        account_id = request.query_params.get('account')
        try:
            account_id = int(account_id) if account_id else None
        except ValueError:
            account_id = None
        data = get_dashboard_data(request.user, account_id=account_id)
        return Response(data)
