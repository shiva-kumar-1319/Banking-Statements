from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from accounts.models import BankAccount


class AccountModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='alice', password='Password123!', email='alice@test.com')
        self.user2 = User.objects.create_user(username='bob', password='Password123!', email='bob@test.com')

    def test_user_registration(self):
        data = {
            'username': 'carol',
            'email': 'carol@test.com',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
            'preferred_currency': 'INR'
        }
        res = self.client.post('/api/auth/register/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', res.data)
        self.assertIn('access', res.data['tokens'])

    def test_jwt_login(self):
        res = self.client.post('/api/auth/login/', {'username': 'alice', 'password': 'Password123!'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)

    def test_masked_account_number(self):
        acc = BankAccount.objects.create(
            user=self.user1,
            name='Salary Account',
            bank_name='HDFC',
            account_number='50100234567890',
            balance=Decimal('25000.00'),
            opening_balance=Decimal('25000.00'),
        )
        self.assertEqual(acc.masked_account_number, '•••• 7890')

    def test_user_data_isolation(self):
        # Alice creates an account
        self.client.force_authenticate(user=self.user1)
        res = self.client.post('/api/accounts/', {
            'name': 'Alice Savings',
            'bank_name': 'Chase',
            'account_number': '1111222233334444',
            'account_type': 'SAVINGS',
            'opening_balance': '1000.00',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        alice_acc_id = res.data['id']

        # Bob logs in and tries to access Alice's account
        self.client.force_authenticate(user=self.user2)
        get_res = self.client.get(f'/api/accounts/{alice_acc_id}/')
        self.assertEqual(get_res.status_code, status.HTTP_404_NOT_FOUND)

        # Bob lists accounts; should not see Alice's account
        list_res = self.client.get('/api/accounts/')
        self.assertEqual(len(list_res.data['results'] if 'results' in list_res.data else list_res.data), 0)
