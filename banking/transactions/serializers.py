from rest_framework import serializers
from .models import Transaction, CATEGORIES


class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.ReadOnlyField(source='account.name')
    bank_name = serializers.ReadOnlyField(source='account.bank_name')
    account_number_masked = serializers.ReadOnlyField(source='account.masked_account_number')
    currency = serializers.ReadOnlyField(source='account.currency')

    class Meta:
        model = Transaction
        fields = [
            'id',
            'account',
            'account_name',
            'bank_name',
            'account_number_masked',
            'currency',
            'statement',
            'date',
            'value_date',
            'description',
            'reference_number',
            'transaction_type',
            'amount',
            'balance_after',
            'category',
            'category_confidence',
            'is_categorized_by_user',
            'notes',
            'is_recurring',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'account_name',
            'bank_name',
            'account_number_masked',
            'currency',
            'statement',
            'created_at',
            'updated_at',
        ]


class TransactionCategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['category', 'notes']

    def update(self, instance, validated_data):
        if 'category' in validated_data and validated_data['category'] != instance.category:
            instance.is_categorized_by_user = True
            instance.category_confidence = 1.0
        return super().update(instance, validated_data)

