from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Transaction, CATEGORIES
from .serializers import TransactionSerializer, TransactionCategoryUpdateSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user)

        # Filters
        account_id = self.request.query_params.get('account')
        if account_id:
            qs = qs.filter(account_id=account_id)

        tx_type = self.request.query_params.get('type')
        if tx_type:
            qs = qs.filter(transaction_type=tx_type.upper())

        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)

        start_date = self.request.query_params.get('start_date')
        if start_date:
            qs = qs.filter(date__gte=start_date)

        end_date = self.request.query_params.get('end_date')
        if end_date:
            qs = qs.filter(date__lte=end_date)

        min_amount = self.request.query_params.get('min_amount')
        if min_amount:
            try:
                qs = qs.filter(amount__gte=float(min_amount))
            except ValueError:
                pass

        max_amount = self.request.query_params.get('max_amount')
        if max_amount:
            try:
                qs = qs.filter(amount__lte=float(max_amount))
            except ValueError:
                pass

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(description__icontains=search) |
                Q(reference_number__icontains=search) |
                Q(notes__icontains=search)
            )

        # Ordering
        ordering = self.request.query_params.get('ordering', '-date')
        if ordering in ['date', '-date', 'amount', '-amount', 'category', '-category']:
            qs = qs.order_by(ordering, '-created_at')
        else:
            qs = qs.order_by('-date', '-created_at')

        return qs

    def perform_create(self, serializer):
        tx = serializer.save(user=self.request.user)
        tx.account.recalculate_balance()

    def perform_update(self, serializer):
        tx = serializer.save()
        tx.account.recalculate_balance()

    def perform_destroy(self, instance):
        account = instance.account
        instance.delete()
        account.recalculate_balance()

    @action(detail=False, methods=['get'])
    def categories(self, request):
        return Response([{"value": cat[0], "label": cat[1]} for cat in CATEGORIES])

    @action(detail=True, methods=['patch'])
    def update_category(self, request, pk=None):
        transaction = self.get_object()
        serializer = TransactionCategoryUpdateSerializer(transaction, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TransactionSerializer(transaction).data)
