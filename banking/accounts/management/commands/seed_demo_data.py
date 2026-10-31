import os
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import BankAccount, UserProfile
from transactions.models import Transaction
from transactions.categorizer import categorize_transaction


class Command(BaseCommand):
    help = 'Seeds realistic synthetic bank accounts, statements, and transactions for demonstration.'

    def handle(self, *args, **options):
        username = 'demo_user'
        password = 'Password123!'
        email = 'demo@banksense.ai'

        user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'first_name': 'Aarav', 'last_name': 'Sharma'})
        user.set_password(password)
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'preferred_currency': 'INR'})

        # Account 1: Salary Checking
        acc1, _ = BankAccount.objects.get_or_create(
            user=user,
            account_number='50100234561024',
            defaults={
                'name': 'Primary Salary Account',
                'bank_name': 'HDFC Bank',
                'account_type': 'CHECKING',
                'currency': 'INR',
                'opening_balance': Decimal('50000.00'),
                'balance': Decimal('50000.00'),
            }
        )

        # Account 2: Personal Savings
        acc2, _ = BankAccount.objects.get_or_create(
            user=user,
            account_number='00010502939821',
            defaults={
                'name': 'Savings & Emergency Reserve',
                'bank_name': 'ICICI Bank',
                'account_type': 'SAVINGS',
                'currency': 'INR',
                'opening_balance': Decimal('25000.00'),
                'balance': Decimal('25000.00'),
            }
        )

        # Clear existing demo transactions to ensure clean idempotency
        Transaction.objects.filter(user=user).delete()

        today = date.today()

        demo_data = [
            # Current Month
            (today - timedelta(days=2), "SWIGGY BANGALORE IN FOOD ORDER #9921", "DEBIT", Decimal('840.00'), acc1),
            (today - timedelta(days=4), "AMAZON RETAIL INDIA ELECTRONICS PURCHASE", "DEBIT", Decimal('4299.00'), acc1),
            (today - timedelta(days=7), "UBER RIDES KORAMANGALA TO INDIRANAGAR", "DEBIT", Decimal('380.00'), acc1),
            (today - timedelta(days=10), "NETFLIX MONTHLY SUBSCRIPTION", "DEBIT", Decimal('649.00'), acc1),
            (today - timedelta(days=12), "APOLLO PHARMACY HEALTHCARE SUPPLIES", "DEBIT", Decimal('1250.00'), acc1),
            (today - timedelta(days=15), "TRANSFER TO LANDLORD APARTMENT RENT", "DEBIT", Decimal('25000.00'), acc1),
            (today - timedelta(days=18), "ATM CASH WDL NFS KORAMANGALA BRANCH", "DEBIT", Decimal('4000.00'), acc1),
            (today - timedelta(days=20), "BESCOM ELECTRICITY UTILITY BILL", "DEBIT", Decimal('2100.00'), acc1),
            (today - timedelta(days=22), "AIRTEL BROADBAND FIBER BILL", "DEBIT", Decimal('1199.00'), acc1),
            (today - timedelta(days=25), "ACH DIRECT DEP CORP PAYROLL SALARY", "CREDIT", Decimal('85000.00'), acc1),
            (today - timedelta(days=27), "ZERODHA BROKING MUTUAL FUND SIP", "DEBIT", Decimal('15000.00'), acc1),

            # Previous Month
            (today - timedelta(days=32), "SWIGGY BANGALORE IN DINNER ORDER", "DEBIT", Decimal('1120.00'), acc1),
            (today - timedelta(days=35), "ZOMATO RESTAURANT DINING", "DEBIT", Decimal('1450.00'), acc1),
            (today - timedelta(days=38), "TRANSFER TO LANDLORD APARTMENT RENT", "DEBIT", Decimal('25000.00'), acc1),
            (today - timedelta(days=41), "NETFLIX MONTHLY SUBSCRIPTION", "DEBIT", Decimal('649.00'), acc1),
            (today - timedelta(days=45), "BESCOM ELECTRICITY UTILITY BILL", "DEBIT", Decimal('1980.00'), acc1),
            (today - timedelta(days=50), "AIRTEL BROADBAND FIBER BILL", "DEBIT", Decimal('1199.00'), acc1),
            (today - timedelta(days=55), "ACH DIRECT DEP CORP PAYROLL SALARY", "CREDIT", Decimal('85000.00'), acc1),
            (today - timedelta(days=57), "ZERODHA BROKING MUTUAL FUND SIP", "DEBIT", Decimal('15000.00'), acc1),

            # Month Before That (3 months ago)
            (today - timedelta(days=65), "TRANSFER TO LANDLORD APARTMENT RENT", "DEBIT", Decimal('25000.00'), acc1),
            (today - timedelta(days=70), "SWIGGY BANGALORE IN LUNCH", "DEBIT", Decimal('690.00'), acc1),
            (today - timedelta(days=75), "NETFLIX MONTHLY SUBSCRIPTION", "DEBIT", Decimal('649.00'), acc1),
            (today - timedelta(days=80), "BESCOM ELECTRICITY UTILITY BILL", "DEBIT", Decimal('2050.00'), acc1),
            (today - timedelta(days=85), "ACH DIRECT DEP CORP PAYROLL SALARY", "CREDIT", Decimal('85000.00'), acc1),
            (today - timedelta(days=88), "FREELANCE DESIGN CLIENT REMITTANCE", "CREDIT", Decimal('22000.00'), acc2),
        ]

        created_txs = 0
        for tx_date, desc, tx_type, amt, acc in demo_data:
            cat, conf = categorize_transaction(desc, tx_type)
            Transaction.objects.create(
                user=user,
                account=acc,
                date=tx_date,
                description=desc,
                transaction_type=tx_type,
                amount=amt,
                category=cat,
                category_confidence=conf,
            )
            created_txs += 1

        acc1.recalculate_balance()
        acc2.recalculate_balance()

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded demo user '{username}' (password: '{password}') with 2 bank accounts and {created_txs} transactions."
        ))

