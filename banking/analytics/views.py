from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .analytics_service import get_dashboard_data, get_financial_insights


class DashboardAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        account_id = request.query_params.get('account')
        try:
            account_id = int(account_id) if account_id else None
        except ValueError:
            account_id = None

        data = get_dashboard_data(request.user, account_id=account_id)
        return Response(data)


class FinancialInsightsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        insights = get_financial_insights(request.user)
        return Response(insights)
