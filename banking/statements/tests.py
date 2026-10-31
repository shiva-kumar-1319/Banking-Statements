import os
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import BankAccount
from statements.models import Statement
from statements.parsers.extractor import extract_statement
from transactions.models import Transaction


class StatementModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='statement_tester', password='Password123!')
        self.client.force_authenticate(user=self.user)
        self.account = BankAccount.objects.create(
            user=self.user,
            name='Test Account',
            bank_name='HDFC',
            account_number='123456789012',
            opening_balance=Decimal('50000.00'),
            balance=Decimal('50000.00'),
        )

        self.samples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sample_statements')
        self.csv_path = os.path.join(self.samples_dir, 'sample_bank_statement.csv')
        self.xlsx_path = os.path.join(self.samples_dir, 'sample_salary_account.xlsx')
        self.pdf_path = os.path.join(self.samples_dir, 'sample_premium_statement.pdf')

    def test_extract_statement_csv(self):
        with open(self.csv_path, 'rb') as f:
            res = extract_statement(f, 'statement.csv')
        self.assertGreater(len(res.transactions), 5)
        self.assertGreater(res.total_credits, Decimal('0.00'))
        self.assertGreater(res.total_debits, Decimal('0.00'))

    def test_extract_statement_xlsx(self):
        with open(self.xlsx_path, 'rb') as f:
            res = extract_statement(f, 'statement.xlsx')
        self.assertGreater(len(res.transactions), 5)

    def test_extract_statement_pdf(self):
        with open(self.pdf_path, 'rb') as f:
            res = extract_statement(f, 'statement.pdf')
        self.assertGreater(len(res.transactions), 5)

    def test_statement_upload_preview_and_confirm(self):
        with open(self.csv_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                name='sample_bank_statement.csv',
                content=f.read(),
                content_type='text/csv'
            )

        # Upload
        res = self.client.post('/api/statements/', {
            'account': self.account.id,
            'file': uploaded_file
        }, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        stmt_id = res.data['id']
        self.assertEqual(res.data['status'], 'PREVIEW_READY')
        self.assertIn('parsed_data', res.data)

        # Confirm import
        confirm_res = self.client.post(f'/api/statements/{stmt_id}/confirm/')
        self.assertEqual(confirm_res.status_code, status.HTTP_200_OK)
        self.assertGreater(confirm_res.data['imported_count'], 0)

        # Verify transactions exist in DB
        tx_count = Transaction.objects.filter(account=self.account).count()
        self.assertEqual(tx_count, confirm_res.data['imported_count'])

        # Verify account balance changed
        self.account.refresh_from_db()
        self.assertNotEqual(self.account.balance, Decimal('50000.00'))
