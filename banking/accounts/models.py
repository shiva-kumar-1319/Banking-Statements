from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class BankAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('SAVINGS', 'Savings Account'),
        ('CHECKING', 'Checking / Current Account'),
        ('CREDIT_CARD', 'Credit Card'),
        ('INVESTMENT', 'Investment / Trading'),
        ('LOAN', 'Loan Account'),
    ]

    CURRENCY_CHOICES = [
        ('INR', 'Indian Rupee (INR)'),
        ('USD', 'US Dollar (USD)'),
        ('EUR', 'Euro (EUR)'),
        ('GBP', 'British Pound (GBP)'),
        ('CAD', 'Canadian Dollar (CAD)'),
        ('AUD', 'Australian Dollar (AUD)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100, default='General Bank')
    account_number = models.CharField(max_length=50)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='SAVINGS')
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='INR')
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'account_number')

    @property
    def masked_account_number(self):
        clean = str(self.account_number).strip()
        if len(clean) > 4:
            return f"•••• {clean[-4:]}"
        return clean

    def recalculate_balance(self):
        from transactions.models import Transaction
        credits_total = self.transactions.filter(transaction_type='CREDIT').aggregate(
            models.Sum('amount')
        )['amount__sum'] or Decimal('0.00')
        debits_total = self.transactions.filter(transaction_type='DEBIT').aggregate(
            models.Sum('amount')
        )['amount__sum'] or Decimal('0.00')
        self.balance = self.opening_balance + credits_total - debits_total
        self.save(update_fields=['balance', 'updated_at'])
        return self.balance

    def __str__(self):
        return f"{self.name} ({self.bank_name} - {self.masked_account_number})"


# Backward compatibility alias
Account = BankAccount


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_currency = models.CharField(max_length=10, default='INR')
    theme = models.CharField(max_length=10, default='light')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
