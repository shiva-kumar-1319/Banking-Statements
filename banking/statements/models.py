from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Statement(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARSING', 'Parsing'),
        ('PREVIEW_READY', 'Preview Ready'),
        ('CONFIRMED', 'Confirmed / Imported'),
        ('FAILED', 'Failed'),
    ]

    FILE_TYPE_CHOICES = [
        ('PDF', 'PDF Document'),
        ('CSV', 'CSV Spreadsheet'),
        ('XLSX', 'Excel Spreadsheet'),
    ]

    RECONCILIATION_CHOICES = [
        ('RECONCILED', 'Reconciled Perfectly'),
        ('DISCREPANCY', 'Reconciliation Discrepancy'),
        ('UNVERIFIED', 'Unverified / No Closing Balance'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='statements')
    account = models.ForeignKey('accounts.BankAccount', on_delete=models.CASCADE, related_name='statements')
    file = models.FileField(upload_to='statements/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    file_size = models.PositiveIntegerField(default=0)
    file_hash = models.CharField(max_length=64, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)

    parsed_data = models.JSONField(default=dict, blank=True)
    extracted_opening_balance = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    extracted_closing_balance = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    total_transactions_count = models.IntegerField(default=0)
    total_credits = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_debits = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    reconciliation_status = models.CharField(max_length=20, choices=RECONCILIATION_CHOICES, default='UNVERIFIED')
    reconciliation_difference = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file_name} ({self.account.name} - {self.status})"
