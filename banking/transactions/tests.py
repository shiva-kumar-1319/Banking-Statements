from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import BankAccount
from transactions.models import Transaction
from transactions.categorizer import categorize_transaction


class TransactionModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='tester', password='Password123!')
        self.client.force_authenticate(user=self.user)
        self.account = BankAccount.objects.create(
            user=self.user,
            name='Primary Checking',
            bank_name='ICICI',
            account_number='992019283746',
            opening_balance=Decimal('10000.00'),
            balance=Decimal('10000.00'),
        )

    def test_categorizer_rules(self):
        cat1, conf1 = categorize_transaction("DIRECT DEP SALARY FOR MAY 2026", "CREDIT")
        self.assertEqual(cat1, "Salary")
        self.assertGreater(conf1, 0.8)

        cat2, _ = categorize_transaction("SWIGGY BANGALORE ORDER #9921", "DEBIT")
        self.assertEqual(cat2, "Food")

        cat3, _ = categorize_transaction("TRANSFER TO LANDLORD APARTMENT RENT", "DEBIT")
        self.assertEqual(cat3, "Rent")

        cat4, _ = categorize_transaction("ATM CASH WDL NFS KORAMANGALA", "DEBIT")
        self.assertEqual(cat4, "ATM withdrawals")

        cat5, _ = categorize_transaction("NETFLIX MONTHLY SUBSCRIPTION", "DEBIT")
        self.assertEqual(cat5, "Entertainment")

    def test_transaction_creation_and_balance_recalculation(self):
        t1 = Transaction.objects.create(
            user=self.user,
            account=self.account,
            date='2026-05-01',
            description='Salary Credit',
            transaction_type='CREDIT',
            amount=Decimal('50000.00'),
            category='Salary',
        )
        self.account.recalculate_balance()
        self.assertEqual(self.account.balance, Decimal('60000.00'))

        t2 = Transaction.objects.create(
            user=self.user,
            account=self.account,
            date='2026-05-02',
            description='Rent payment',
            transaction_type='DEBIT',
            amount=Decimal('20000.00'),
            category='Rent',
        )
        self.account.recalculate_balance()
        self.assertEqual(self.account.balance, Decimal('40000.00'))

    def test_transaction_filtering_and_search(self):
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            date='2026-05-01',
            description='Swiggy dinner',
            transaction_type='DEBIT',
            amount=Decimal('1200.00'),
            category='Food',
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            date='2026-05-02',
            description='Amazon electronics shopping',
            transaction_type='DEBIT',
            amount=Decimal('5000.00'),
            category='Shopping',
        )

        res = self.client.get('/api/transactions/?category=Food')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data['results'] if 'results' in res.data else res.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['category'], 'Food')

        search_res = self.client.get('/api/transactions/?search=electronics')
        s_results = search_res.data['results'] if 'results' in search_res.data else search_res.data
        self.assertEqual(len(s_results), 1)
        self.assertEqual(s_results[0]['category'], 'Shopping')
