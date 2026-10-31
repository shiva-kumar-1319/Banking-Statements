from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from django.db.models import Sum, Count, Avg
from django.contrib.auth.models import User
from accounts.models import BankAccount
from transactions.models import Transaction, CATEGORIES
from statements.models import Statement


def get_dashboard_data(user: User, account_id: int = None) -> Dict[str, Any]:
    # 1. Accounts
    accounts_qs = BankAccount.objects.filter(user=user, is_active=True)
    if account_id:
        accounts_qs = accounts_qs.filter(id=account_id)

    total_balance = sum((acc.balance for acc in accounts_qs), Decimal('0.00'))

    # 2. Transactions
    tx_qs = Transaction.objects.filter(user=user)
    if account_id:
        tx_qs = tx_qs.filter(account_id=account_id)

    total_income = tx_qs.filter(transaction_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_expenses = tx_qs.filter(transaction_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    net_savings = total_income - total_expenses
    savings_rate = round(float((net_savings / total_income) * 100), 1) if total_income > Decimal('0.00') else 0.0

    # 3. Monthly Trends (last 6 months)
    monthly_data: Dict[str, Dict[str, Decimal]] = {}
    today = date.today()
    # Initialize last 6 months keys
    for i in range(5, -1, -1):
        # Approximate month calculation
        m_date = today.replace(day=1) - timedelta(days=i * 28)
        key = m_date.strftime('%Y-%m')
        monthly_data[key] = {'income': Decimal('0.00'), 'expense': Decimal('0.00'), 'net': Decimal('0.00')}

    for tx in tx_qs.filter(date__gte=today - timedelta(days=180)):
        key = tx.date.strftime('%Y-%m')
        if key not in monthly_data:
            monthly_data[key] = {'income': Decimal('0.00'), 'expense': Decimal('0.00'), 'net': Decimal('0.00')}
        if tx.transaction_type == 'CREDIT':
            monthly_data[key]['income'] += tx.amount
        else:
            monthly_data[key]['expense'] += tx.amount

    monthly_trends = []
    for k in sorted(monthly_data.keys()):
        inc = monthly_data[k]['income']
        exp = monthly_data[k]['expense']
        net = inc - exp
        try:
            m_label = datetime.strptime(k, '%Y-%m').strftime('%b %Y')
        except ValueError:
            m_label = k
        monthly_trends.append({
            'month': k,
            'label': m_label,
            'income': float(inc),
            'expense': float(exp),
            'net': float(net),
        })

    # 4. Spending by Category (Debits)
    category_totals = tx_qs.filter(transaction_type='DEBIT').values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    category_breakdown = []
    exp_float = float(total_expenses)
    for c in category_totals:
        amt = float(c['total'])
        pct = round((amt / exp_float * 100), 1) if exp_float > 0 else 0
        category_breakdown.append({
            'category': c['category'],
            'amount': amt,
            'percentage': pct,
            'count': c['count'],
        })

    # 5. Daily Activity (last 30 days)
    daily_map = {}
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        daily_map[d_str] = {'date': d_str, 'income': 0.0, 'expense': 0.0, 'count': 0}

    for tx in tx_qs.filter(date__gte=today - timedelta(days=30)):
        d_str = tx.date.strftime('%Y-%m-%d')
        if d_str in daily_map:
            daily_map[d_str]['count'] += 1
            if tx.transaction_type == 'CREDIT':
                daily_map[d_str]['income'] += float(tx.amount)
            else:
                daily_map[d_str]['expense'] += float(tx.amount)

    daily_activity = sorted(daily_map.values(), key=lambda x: x['date'])

    # 6. Recent Transactions (last 10)
    recent_transactions = [
        {
            'id': t.id,
            'date': t.date.isoformat(),
            'description': t.description,
            'category': t.category,
            'transaction_type': t.transaction_type,
            'amount': float(t.amount),
            'account_name': t.account.name,
            'bank_name': t.account.bank_name,
            'currency': t.account.currency,
        }
        for t in tx_qs.select_related('account')[:10]
    ]

    # 7. Account summaries
    accounts_list = [
        {
            'id': acc.id,
            'name': acc.name,
            'bank_name': acc.bank_name,
            'masked_account_number': acc.masked_account_number,
            'account_type': acc.account_type,
            'currency': acc.currency,
            'balance': float(acc.balance),
        }
        for acc in BankAccount.objects.filter(user=user, is_active=True)
    ]

    # 8. Statements overview
    statements_list = [
        {
            'id': s.id,
            'file_name': s.file_name,
            'file_type': s.file_type,
            'account_name': s.account.name,
            'status': s.status,
            'total_transactions': s.total_transactions_count,
            'uploaded_at': s.uploaded_at.isoformat(),
            'reconciliation_status': s.reconciliation_status,
        }
        for s in Statement.objects.filter(user=user).select_related('account')[:5]
    ]

    preferred_currency = 'INR'
    if hasattr(user, 'profile'):
        preferred_currency = user.profile.preferred_currency

    return {
        'total_balance': float(total_balance),
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'net_savings': float(net_savings),
        'savings_rate': savings_rate,
        'preferred_currency': preferred_currency,
        'monthly_trends': monthly_trends,
        'category_breakdown': category_breakdown,
        'daily_activity': daily_activity,
        'recent_transactions': recent_transactions,
        'accounts': accounts_list,
        'statements': statements_list,
        'transaction_count': tx_qs.count(),
    }


def get_financial_insights(user: User) -> Dict[str, Any]:
    tx_qs = Transaction.objects.filter(user=user)
    total_expenses = tx_qs.filter(transaction_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Top spending categories
    category_totals = tx_qs.filter(transaction_type='DEBIT').values('category').annotate(
        total=Sum('amount'), count=Count('id')
    ).order_by('-total')[:5]

    top_categories = []
    for c in category_totals:
        pct = round(float(c['total'] / total_expenses * 100), 1) if total_expenses > Decimal('0.00') else 0
        top_categories.append({
            'category': c['category'],
            'amount': float(c['total']),
            'percentage': pct,
            'count': c['count'],
        })

    # Recurring transaction detection
    # Group debits by lower-cased description words / merchants appearing in 2+ separate months
    merchants: Dict[str, List[Transaction]] = {}
    for tx in tx_qs.filter(transaction_type='DEBIT'):
        # Normalize key
        desc_key = tx.description.strip().lower()[:25]
        if desc_key not in merchants:
            merchants[desc_key] = []
        merchants[desc_key].append(tx)

    recurring_transactions = []
    for desc_key, items in merchants.items():
        if len(items) >= 2:
            months = set(i.date.strftime('%Y-%m') for i in items)
            if len(months) >= 2:
                avg_amt = sum((i.amount for i in items), Decimal('0.00')) / Decimal(len(items))
                recurring_transactions.append({
                    'merchant_sample': items[0].description,
                    'category': items[0].category,
                    'occurrences': len(items),
                    'average_amount': float(round(avg_amt, 2)),
                    'months_active': sorted(list(months)),
                    'is_subscription_pattern': any(k in desc_key for k in ['netflix', 'spotify', 'prime', 'broadband', 'rent', 'wifi', 'gym']),
                })

    recurring_transactions.sort(key=lambda x: x['average_amount'], reverse=True)

    # Unusual spending detection (Anomalies)
    debits = list(tx_qs.filter(transaction_type='DEBIT').order_by('-amount'))
    anomalies = []
    if debits:
        amounts = [float(t.amount) for t in debits]
        mean_amt = sum(amounts) / len(amounts)
        threshold = max(mean_amt * 2.5, 5000.0)  # at least 2.5x mean

        for tx in debits:
            amt = float(tx.amount)
            if amt >= threshold:
                anomalies.append({
                    'id': tx.id,
                    'date': tx.date.isoformat(),
                    'description': tx.description,
                    'category': tx.category,
                    'amount': amt,
                    'account_name': tx.account.name,
                    'severity': 'HIGH' if amt >= threshold * 1.5 else 'MEDIUM',
                    'reason': f"Amount of {amt:,.2f} is significantly higher than your typical average transaction ({mean_amt:,.2f}).",
                })
            if len(anomalies) >= 6:
                break

    # Month over month comparison
    today = date.today()
    curr_month_str = today.strftime('%Y-%m')
    prev_month_date = today.replace(day=1) - timedelta(days=1)
    prev_month_str = prev_month_date.strftime('%Y-%m')

    curr_exp = tx_qs.filter(transaction_type='DEBIT', date__startswith=curr_month_str).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    prev_exp = tx_qs.filter(transaction_type='DEBIT', date__startswith=prev_month_str).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    exp_change_pct = 0.0
    if prev_exp > Decimal('0.00'):
        exp_change_pct = round(float((curr_exp - prev_exp) / prev_exp * 100), 1)

    return {
        'top_categories': top_categories,
        'recurring_transactions': recurring_transactions[:8],
        'unusual_transactions': anomalies,
        'month_over_month': {
            'current_month': curr_month_str,
            'current_month_expenses': float(curr_exp),
            'previous_month': prev_month_str,
            'previous_month_expenses': float(prev_exp),
            'expense_change_percentage': exp_change_pct,
            'trend': 'INCREASED' if exp_change_pct > 0 else ('DECREASED' if exp_change_pct < 0 else 'FLAT'),
        },
    }

