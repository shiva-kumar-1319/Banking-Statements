from rest_framework import serializers
from .models import Statement
from accounts.models import BankAccount


class StatementSerializer(serializers.ModelSerializer):
    account_name = serializers.ReadOnlyField(source='account.name')
    bank_name = serializers.ReadOnlyField(source='account.bank_name')
    account_number_masked = serializers.ReadOnlyField(source='account.masked_account_number')

    class Meta:
        model = Statement
        fields = [
            'id',
            'account',
            'account_name',
            'bank_name',
            'account_number_masked',
            'file',
            'file_name',
            'file_type',
            'file_size',
            'file_hash',
            'uploaded_at',
            'status',
            'error_message',
            'total_transactions_count',
            'total_credits',
            'total_debits',
            'extracted_opening_balance',
            'extracted_closing_balance',
            'reconciliation_status',
            'reconciliation_difference',
        ]
        read_only_fields = [
            'id',
            'file_name',
            'file_type',
            'file_size',
            'file_hash',
            'uploaded_at',
            'status',
            'error_message',
            'total_transactions_count',
            'total_credits',
            'total_debits',
            'extracted_opening_balance',
            'extracted_closing_balance',
            'reconciliation_status',
            'reconciliation_difference',
        ]


class StatementDetailSerializer(StatementSerializer):
    class Meta(StatementSerializer.Meta):
        fields = StatementSerializer.Meta.fields + ['parsed_data']

