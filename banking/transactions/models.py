from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import hashlib


CATEGORIES = [
    ('Salary', 'Salary & Income'),
    ('Food', 'Food & Dining'),
    ('Shopping', 'Shopping & Retail'),
    ('Rent', 'Rent & Housing'),
    ('Bills', 'Bills & Utilities'),
    ('Travel', 'Travel & Transportation'),
    ('Entertainment', 'Entertainment & Leisure'),
    ('Healthcare', 'Healthcare & Medical'),
    ('Transfers', 'Transfers & Remittance'),
    ('ATM withdrawals', 'ATM Withdrawals'),
    ('Investments', 'Investments & Savings'),
    ('Other', 'Other / Miscellaneous'),
]


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('DEBIT', 'Debit (Expense)'),
        ('CREDIT', 'Credit (Income)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey('accounts.BankAccount', on_delete=models.CASCADE, related_name='transactions')
    statement = models.ForeignKey(
        'statements.Statement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    date = models.DateField(db_index=True)
    value_date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=500)
    reference_number = models.CharField(max_length=150, blank=True, null=True)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES, db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    balance_after = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    category = models.CharField(max_length=50, choices=CATEGORIES, default='Other', db_index=True)
    category_confidence = models.FloatField(default=1.0)
    is_categorized_by_user = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)

    transaction_hash = models.CharField(max_length=64, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'transaction_type']),
        ]

    def save(self, *args, **kwargs):
        if not self.transaction_hash:
            # Deterministic hash to detect duplicate transaction items in account
            token = f"{self.account_id}_{self.date}_{self.amount}_{self.transaction_type}_{self.description.strip().lower()}"
            self.transaction_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        sign = "+" if self.transaction_type == "CREDIT" else "-"
        return f"{self.date} | {self.category} | {sign}{self.amount} | {self.description[:40]}"
