import hashlib
import os
from decimal import Decimal
from datetime import datetime

from django.db import transaction as db_transaction
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Statement
from .serializers import StatementSerializer, StatementDetailSerializer
from .parsers.extractor import extract_statement
from accounts.models import BankAccount
from transactions.models import Transaction


class StatementViewSet(viewsets.ModelViewSet):
    serializer_class = StatementSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Statement.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'preview']:
            return StatementDetailSerializer
        return StatementSerializer

    def create(self, request, *args, **kwargs):
        account_id = request.data.get('account')
        file_obj = request.FILES.get('file')

        if not account_id:
            return Response({"error": "Please select a bank account for this statement."}, status=status.HTTP_400_BAD_REQUEST)
        if not file_obj:
            return Response({"error": "No file was uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        # Check account ownership
        try:
            account = BankAccount.objects.get(id=account_id, user=request.user)
        except BankAccount.DoesNotExist:
            return Response({"error": "Selected bank account not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

        # Check file extension
        ext = os.path.splitext(file_obj.name)[1].lower()
        if ext not in ['.pdf', '.csv', '.xlsx', '.xls']:
            return Response(
                {"error": f"Unsupported file extension '{ext}'. Please upload a PDF, CSV, or Excel file."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # File size check (max 10MB)
        if file_obj.size > 10 * 1024 * 1024:
            return Response({"error": "File size exceeds the 10MB limit."}, status=status.HTTP_400_BAD_REQUEST)

        # Compute SHA-256 hash for duplicate detection
        hasher = hashlib.sha256()
        for chunk in file_obj.chunks():
            hasher.update(chunk)
        file_hash = hasher.hexdigest()

        # Check if already uploaded and confirmed for this account
        duplicate = Statement.objects.filter(user=request.user, account=account, file_hash=file_hash, status='CONFIRMED').first()
        if duplicate:
            return Response(
                {"error": f"This statement ('{duplicate.file_name}') has already been uploaded and imported for this account."},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_type = 'PDF' if ext == '.pdf' else ('CSV' if ext == '.csv' else 'XLSX')

        statement = Statement.objects.create(
            user=request.user,
            account=account,
            file=file_obj,
            file_name=file_obj.name,
            file_type=file_type,
            file_size=file_obj.size,
            file_hash=file_hash,
            status='PARSING'
        )

        # Perform extraction
        try:
            # Open file stream from storage
            statement.file.open('rb')
            result = extract_statement(statement.file, statement.file_name)
            statement.file.close()

            statement.parsed_data = result.to_dict()
            statement.total_transactions_count = len(result.transactions)
            statement.total_credits = result.total_credits
            statement.total_debits = result.total_debits
            statement.extracted_opening_balance = result.opening_balance
            statement.extracted_closing_balance = result.closing_balance
            statement.reconciliation_status = result.reconciliation_status
            statement.reconciliation_difference = result.reconciliation_difference
            statement.status = 'PREVIEW_READY'
            statement.save()

            return Response(StatementDetailSerializer(statement).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            statement.status = 'FAILED'
            statement.error_message = f"Error during statement extraction: {str(e)}"
            statement.save()
            return Response(
                {"error": statement.error_message, "statement_id": statement.id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        statement = self.get_object()
        return Response(StatementDetailSerializer(statement).data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirms import of transactions from the statement preview into persistent storage.
        Allows user to provide custom adjusted transaction rows.
        """
        statement = self.get_object()
        if statement.status == 'CONFIRMED':
            return Response({"error": "This statement has already been confirmed and imported."}, status=status.HTTP_400_BAD_REQUEST)

        # Allow user to submit adjusted preview list or fallback to stored parsed_data
        tx_list = request.data.get('transactions') or statement.parsed_data.get('transactions', [])

        if not tx_list:
            return Response({"error": "No transactions found to import."}, status=status.HTTP_400_BAD_REQUEST)

        created_count = 0
        skipped_count = 0

        with db_transaction.atomic():
            for item in tx_list:
                try:
                    d_val = item.get('date')
                    parsed_date = datetime.strptime(d_val[:10], '%Y-%m-%d').date() if isinstance(d_val, str) else d_val
                except Exception:
                    continue

                amt = Decimal(str(item.get('amount', '0.00')))
                t_type = item.get('transaction_type', 'DEBIT').upper()
                desc = item.get('description', 'Transaction').strip()
                ref = item.get('reference_number')
                cat = item.get('category', 'Other')
                bal_after = Decimal(str(item.get('balance_after'))) if item.get('balance_after') is not None else None

                # Generate duplicate check token
                token = f"{statement.account_id}_{parsed_date}_{amt}_{t_type}_{desc.lower()}"
                tx_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()

                # Check if this exact transaction exists
                if Transaction.objects.filter(account=statement.account, transaction_hash=tx_hash).exists():
                    skipped_count += 1
                    continue

                Transaction.objects.create(
                    user=request.user,
                    account=statement.account,
                    statement=statement,
                    date=parsed_date,
                    description=desc,
                    reference_number=ref,
                    transaction_type=t_type,
                    amount=amt,
                    balance_after=bal_after,
                    category=cat,
                    category_confidence=item.get('confidence', 1.0),
                    is_categorized_by_user=item.get('is_categorized_by_user', False),
                    transaction_hash=tx_hash,
                )
                created_count += 1

            statement.status = 'CONFIRMED'
            statement.save()

            # Update account opening balance if account currently has 0.00 and statement has opening balance
            if statement.extracted_opening_balance is not None and statement.account.opening_balance == Decimal('0.00'):
                statement.account.opening_balance = statement.extracted_opening_balance
                statement.account.save(update_fields=['opening_balance'])

            # Recalculate account balance
            new_balance = statement.account.recalculate_balance()

        return Response({
            "message": f"Successfully imported {created_count} transactions ({skipped_count} duplicates skipped).",
            "imported_count": created_count,
            "skipped_count": skipped_count,
            "account_balance": str(new_balance),
            "statement": StatementSerializer(statement).data,
        })
