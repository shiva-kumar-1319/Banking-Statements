from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import re
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from transactions.models import Transaction, CATEGORIES
from accounts.models import BankAccount


def identify_intent(query: str) -> str:
    q = query.lower().strip()

    if any(k in q for k in ['spend this month', 'spent this month', 'this month expenses', 'expenses this month']):
        return 'SPEND_THIS_MONTH'
    if any(k in q for k in ['highest category', 'highest expenditure', 'top category', 'most spent on', 'where did i spend most']):
        return 'HIGHEST_CATEGORY'
    if any(k in q for k in ['top five', 'top 5', 'top expenses', 'biggest expenses', 'largest transactions']):
        return 'TOP_EXPENSES'
    if any(k in q for k in ['compare', 'last month vs', 'month over month', 'this month with last']):
        return 'COMPARE_MONTHS'
    if any(k in q for k in ['salary', 'paycheck', 'payroll', 'wages']):
        return 'SALARY_CREDITED'
    if any(k in q for k in ['unusual', 'anomaly', 'anomalies', 'strange', 'suspicious', 'large transaction']):
        return 'UNUSUAL_TRANSACTIONS'
    if any(k in q for k in ['save', 'savings', 'last three months', 'last 3 months']):
        return 'SAVINGS_THREE_MONTHS'
    if any(k in q for k in ['balance', 'how much money', 'total balance', 'account balance']):
        return 'ACCOUNT_BALANCE'
    if any(k in q for k in ['food', 'dining', 'swiggy', 'zomato']):
        return 'CATEGORY_FOOD'
    if any(k in q for k in ['travel', 'cab', 'uber', 'flight', 'petrol']):
        return 'CATEGORY_TRAVEL'
    if any(k in q for k in ['shopping', 'amazon', 'flipkart']):
        return 'CATEGORY_SHOPPING'
    if any(k in q for k in ['bills', 'electricity', 'broadband', 'recharge']):
        return 'CATEGORY_BILLS'
    if any(k in q for k in ['rent']):
        return 'CATEGORY_RENT'

    return 'GENERAL_SUMMARY'


def ground_query(user: User, query: str) -> Dict[str, Any]:
    """
    Deterministically computes financial figures required to ground the query.
    """
    intent = identify_intent(query)
    today = date.today()
    curr_month_str = today.strftime('%Y-%m')
    curr_month_label = today.strftime('%B %Y')

    first_day_curr = today.replace(day=1)
    prev_month_date = first_day_curr - timedelta(days=1)
    prev_month_str = prev_month_date.strftime('%Y-%m')
    prev_month_label = prev_month_date.strftime('%B %Y')

    user_txs = Transaction.objects.filter(user=user)
    currency = 'INR'
    if hasattr(user, 'profile'):
        currency = user.profile.preferred_currency

    if intent == 'SPEND_THIS_MONTH':
        month_debits = user_txs.filter(transaction_type='DEBIT', date__startswith=curr_month_str)
        total_spent = month_debits.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        count = month_debits.count()

        by_cat = month_debits.values('category').annotate(total=Sum('amount')).order_by('-total')[:3]

        return {
            'intent': intent,
            'timeframe': curr_month_label,
            'total_spent': float(total_spent),
            'transaction_count': count,
            'top_categories_this_month': [{'category': c['category'], 'amount': float(c['total'])} for c in by_cat],
            'currency': currency,
        }

    elif intent == 'HIGHEST_CATEGORY':
        cat_agg = user_txs.filter(transaction_type='DEBIT').values('category').annotate(
            total=Sum('amount'), count=Count('id')
        ).order_by('-total')

        top_cat = cat_agg.first()
        total_exp = user_txs.filter(transaction_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        return {
            'intent': intent,
            'highest_category': top_cat['category'] if top_cat else 'None',
            'highest_category_amount': float(top_cat['total']) if top_cat else 0.0,
            'highest_category_count': top_cat['count'] if top_cat else 0,
            'percentage_of_all_expenses': round(float(top_cat['total'] / total_exp * 100), 1) if top_cat and total_exp > 0 else 0.0,
            'all_categories': [{'category': c['category'], 'amount': float(c['total'])} for c in cat_agg[:5]],
            'currency': currency,
        }

    elif intent == 'TOP_EXPENSES':
        top_txs = user_txs.filter(transaction_type='DEBIT').order_by('-amount')[:5]
        return {
            'intent': intent,
            'top_transactions': [
                {
                    'date': t.date.isoformat(),
                    'description': t.description,
                    'amount': float(t.amount),
                    'category': t.category,
                    'account': t.account.name,
                }
                for t in top_txs
            ],
            'currency': currency,
        }

    elif intent == 'COMPARE_MONTHS':
        curr_debit = user_txs.filter(transaction_type='DEBIT', date__startswith=curr_month_str).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        prev_debit = user_txs.filter(transaction_type='DEBIT', date__startswith=prev_month_str).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        curr_income = user_txs.filter(transaction_type='CREDIT', date__startswith=curr_month_str).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        prev_income = user_txs.filter(transaction_type='CREDIT', date__startswith=prev_month_str).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        diff = curr_debit - prev_debit
        pct = round(float(diff / prev_debit * 100), 1) if prev_debit > 0 else 0.0

        return {
            'intent': intent,
            'current_month_label': curr_month_label,
            'previous_month_label': prev_month_label,
            'current_month_expenses': float(curr_debit),
            'previous_month_expenses': float(prev_debit),
            'current_month_income': float(curr_income),
            'previous_month_income': float(prev_income),
            'difference_amount': float(abs(diff)),
            'percentage_change': pct,
            'direction': 'increased' if diff > 0 else ('decreased' if diff < 0 else 'unchanged'),
            'currency': currency,
        }

    elif intent == 'SALARY_CREDITED':
        salary_txs = user_txs.filter(
            transaction_type='CREDIT'
        ).filter(
            Q(category='Salary') |
            Q(description__icontains='salary') |
            Q(description__icontains='payroll') |
            Q(description__icontains='corp pay')
        ).order_by('-date')

        total_salary = salary_txs.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        recent_salaries = [
            {'date': t.date.isoformat(), 'amount': float(t.amount), 'description': t.description, 'account': t.account.name}
            for t in salary_txs[:5]
        ]

        return {
            'intent': intent,
            'total_salary_credited': float(total_salary),
            'total_salary_count': salary_txs.count(),
            'recent_salary_transactions': recent_salaries,
            'currency': currency,
        }

    elif intent == 'UNUSUAL_TRANSACTIONS':
        debits = list(user_txs.filter(transaction_type='DEBIT').order_by('-amount'))
        unusual = []
        if debits:
            amounts = [float(t.amount) for t in debits]
            mean_amt = sum(amounts) / len(amounts)
            threshold = max(mean_amt * 2.2, 5000.0)
            for t in debits:
                amt = float(t.amount)
                if amt >= threshold:
                    unusual.append({
                        'date': t.date.isoformat(),
                        'description': t.description,
                        'amount': amt,
                        'category': t.category,
                        'account': t.account.name,
                    })
                if len(unusual) >= 5:
                    break

        return {
            'intent': intent,
            'unusual_transactions': unusual,
            'threshold_used': threshold if debits else 0.0,
            'currency': currency,
        }

    elif intent == 'SAVINGS_THREE_MONTHS':
        three_months_ago = today - timedelta(days=90)
        recent_txs = user_txs.filter(date__gte=three_months_ago)
        income_3m = recent_txs.filter(transaction_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        expense_3m = recent_txs.filter(transaction_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        net_saved = income_3m - expense_3m
        rate = round(float(net_saved / income_3m * 100), 1) if income_3m > 0 else 0.0

        return {
            'intent': intent,
            'timeframe': f"Last 3 Months ({three_months_ago.strftime('%b %d, %Y')} to {today.strftime('%b %d, %Y')})",
            'total_income': float(income_3m),
            'total_expenses': float(expense_3m),
            'net_savings': float(net_saved),
            'savings_rate': rate,
            'currency': currency,
        }

    elif intent == 'ACCOUNT_BALANCE':
        accounts = BankAccount.objects.filter(user=user, is_active=True)
        acc_list = [
            {'name': a.name, 'bank': a.bank_name, 'masked_number': a.masked_account_number, 'balance': float(a.balance)}
            for a in accounts
        ]
        total_bal = sum(a['balance'] for a in acc_list)
        return {
            'intent': intent,
            'total_balance': total_bal,
            'accounts': acc_list,
            'currency': currency,
        }

    elif intent.startswith('CATEGORY_'):
        cat_name = intent.replace('CATEGORY_', '').capitalize()
        # Find exact category name
        matched_cat = next((c[0] for c in CATEGORIES if c[0].lower() == cat_name.lower()), cat_name)
        cat_txs = user_txs.filter(transaction_type='DEBIT', category__iexact=matched_cat).order_by('-date')
        total_cat = cat_txs.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        return {
            'intent': intent,
            'category': matched_cat,
            'total_spent': float(total_cat),
            'count': cat_txs.count(),
            'recent_transactions': [
                {'date': t.date.isoformat(), 'description': t.description, 'amount': float(t.amount)}
                for t in cat_txs[:5]
            ],
            'currency': currency,
        }

    else:
        # GENERAL_SUMMARY
        total_income = user_txs.filter(transaction_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        total_expenses = user_txs.filter(transaction_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        net = total_income - total_expenses
        total_balance = sum((a.balance for a in BankAccount.objects.filter(user=user, is_active=True)), Decimal('0.00'))

        top_cats = user_txs.filter(transaction_type='DEBIT').values('category').annotate(total=Sum('amount')).order_by('-total')[:3]

        return {
            'intent': 'GENERAL_SUMMARY',
            'total_balance': float(total_balance),
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'net_savings': float(net),
            'top_categories': [{'category': c['category'], 'amount': float(c['total'])} for c in top_cats],
            'transaction_count': user_txs.count(),
            'currency': currency,
        }

