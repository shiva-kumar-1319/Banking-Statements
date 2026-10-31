from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import BankAccount
from transactions.models import Transaction
from assistant.query_grounding import ground_query
from assistant.assistant_service import ask_ai_assistant


class AssistantAndAnalyticsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='ai_user', password='Password123!')
        self.client.force_authenticate(user=self.user)
        self.account = BankAccount.objects.create(
            user=self.user,
            name='Savings',
            bank_name='SBI',
            account_number='000011112222',
            opening_balance=Decimal('10000.00'),
            balance=Decimal('10000.00'),
        )

        Transaction.objects.create(
            user=self.user,
            account=self.account,
            date='2026-05-01',
            description='Payroll Corp Salary',
            transaction_type='CREDIT',
            amount=Decimal('80000.00'),
            category='Salary',
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            date='2026-05-02',
            description='Swiggy food order',
            transaction_type='DEBIT',
            amount=Decimal('1500.00'),
            category='Food',
        )
        Transaction.objects.create(
            user=self.user,
            account=self.account,
            date='2026-05-03',
            description='Apartment rent payment',
            transaction_type='DEBIT',
            amount=Decimal('25000.00'),
            category='Rent',
        )
        self.account.recalculate_balance()

    def test_analytics_dashboard_endpoint(self):
        res = self.client.get('/api/analytics/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(res.data['total_income'], 80000.00)
        self.assertAlmostEqual(res.data['total_expenses'], 26500.00)
        self.assertAlmostEqual(res.data['net_savings'], 53500.00)

    def test_query_grounding_spend_intent(self):
        facts = ground_query(self.user, "How much did I spend on food?")
        self.assertEqual(facts['intent'], 'CATEGORY_FOOD')
        self.assertAlmostEqual(facts['total_spent'], 1500.00)

    def test_query_grounding_salary_intent(self):
        facts = ground_query(self.user, "How much salary was credited?")
        self.assertEqual(facts['intent'], 'SALARY_CREDITED')
        self.assertAlmostEqual(facts['total_salary_credited'], 80000.00)

    def test_assistant_chat_endpoint(self):
        res = self.client.post('/api/assistant/chat/', {'message': 'What were my top five expenses?'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('response', res.data)
        self.assertIn('grounded_facts', res.data)
        # Verify deterministic figures are in response text
        self.assertIn('Rent', res.data['response'])
