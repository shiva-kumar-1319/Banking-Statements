import io
import csv
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any

from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from transactions.models import Transaction
from accounts.models import BankAccount


def generate_csv_report(user: User, params: Dict[str, Any]) -> HttpResponse:
    qs = Transaction.objects.filter(user=user)

    account_id = params.get('account')
    if account_id:
        qs = qs.filter(account_id=account_id)

    category = params.get('category')
    if category:
        qs = qs.filter(category=category)

    tx_type = params.get('type')
    if tx_type:
        qs = qs.filter(transaction_type=tx_type.upper())

    start_date = params.get('start_date')
    if start_date:
        qs = qs.filter(date__gte=start_date)

    end_date = params.get('end_date')
    if end_date:
        qs = qs.filter(date__lte=end_date)

    qs = qs.select_related('account').order_by('-date')

    response = HttpResponse(content_type='text/csv')
    filename = f"banksense_transactions_{date.today().strftime('%Y%m%d')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'Transaction ID',
        'Date',
        'Account Name',
        'Bank Name',
        'Masked Account',
        'Description',
        'Reference Number',
        'Type',
        'Amount',
        'Balance After',
        'Category',
        'Notes',
    ])

    for t in qs:
        writer.writerow([
            t.id,
            t.date.isoformat(),
            t.account.name,
            t.account.bank_name,
            t.account.masked_account_number,
            t.description,
            t.reference_number or '',
            t.transaction_type,
            str(t.amount),
            str(t.balance_after) if t.balance_after is not None else '',
            t.category,
            t.notes or '',
        ])

    return response


def generate_pdf_report(user: User, params: Dict[str, Any]) -> HttpResponse:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=14,
    )
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=12,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("BankSense AI — Financial Statement Report", title_style))
    today_str = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    elements.append(Paragraph(f"Generated for: <b>{user.get_full_name() or user.username}</b> &nbsp;|&nbsp; Generated on: {today_str}", subtitle_style))
    elements.append(Spacer(1, 10))

    # Metric summaries
    tx_qs = Transaction.objects.filter(user=user)
    account_id = params.get('account')
    if account_id:
        tx_qs = tx_qs.filter(account_id=account_id)

    total_income = tx_qs.filter(transaction_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_expenses = tx_qs.filter(transaction_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    net_savings = total_income - total_expenses
    savings_rate = round(float((net_savings / total_income) * 100), 1) if total_income > Decimal('0.00') else 0.0

    accounts = BankAccount.objects.filter(user=user, is_active=True)
    if account_id:
        accounts = accounts.filter(id=account_id)
    total_balance = sum((a.balance for a in accounts), Decimal('0.00'))

    currency = 'INR'
    if hasattr(user, 'profile'):
        currency = user.profile.preferred_currency
    sym = '₹' if currency == 'INR' else '$'

    elements.append(Paragraph("1. Executive Financial Summary", heading_style))

    summary_data = [
        ['Metric', 'Amount', 'Metric', 'Amount'],
        ['Total Balance', f"{sym}{total_balance:,.2f}", 'Savings Rate', f"{savings_rate}%"],
        ['Total Income', f"{sym}{total_income:,.2f}", 'Net Savings', f"{sym}{net_savings:,.2f}"],
        ['Total Expenses', f"{sym}{total_expenses:,.2f}", 'Total Transactions', str(tx_qs.count())],
    ]
    summary_table = Table(summary_data, colWidths=[130, 130, 130, 130])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 14))

    # Accounts Table
    elements.append(Paragraph("2. Connected Bank Accounts", heading_style))
    acc_rows = [['Account Name', 'Bank', 'Account Number', 'Type', 'Current Balance']]
    for a in accounts:
        acc_rows.append([
            a.name,
            a.bank_name,
            a.masked_account_number,
            a.get_account_type_display(),
            f"{sym}{a.balance:,.2f}"
        ])
    acc_table = Table(acc_rows, colWidths=[120, 110, 110, 80, 100])
    acc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
    ]))
    elements.append(acc_table)
    elements.append(Spacer(1, 14))

    # Spending by Category
    elements.append(Paragraph("3. Category-wise Spending Breakdown", heading_style))
    cat_qs = tx_qs.filter(transaction_type='DEBIT').values('category').annotate(
        total=Sum('amount'), count=Count('id')
    ).order_by('-total')

    cat_rows = [['Category', 'Transactions', 'Total Spent', '% of Total Expenses']]
    exp_float = float(total_expenses)
    for c in cat_qs:
        amt = float(c['total'])
        pct = round(amt / exp_float * 100, 1) if exp_float > 0 else 0
        cat_rows.append([
            c['category'],
            str(c['count']),
            f"{sym}{amt:,.2f}",
            f"{pct}%"
        ])

    if len(cat_rows) == 1:
        cat_rows.append(['No expenses recorded', '0', f"{sym}0.00", '0%'])

    cat_table = Table(cat_rows, colWidths=[160, 100, 130, 130])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
    ]))
    elements.append(cat_table)
    elements.append(Spacer(1, 14))

    # Recent Transactions Table (Top 15)
    elements.append(Paragraph("4. Recent Transactions Overview", heading_style))
    tx_rows = [['Date', 'Description', 'Category', 'Type', 'Amount']]
    for t in tx_qs[:15]:
        tx_rows.append([
            t.date.strftime('%Y-%m-%d'),
            t.description[:28] + ('...' if len(t.description) > 28 else ''),
            t.category,
            t.transaction_type,
            f"{'+' if t.transaction_type == 'CREDIT' else '-'}{sym}{t.amount:,.2f}"
        ])

    if len(tx_rows) == 1:
        tx_rows.append(['-', 'No transactions recorded', '-', '-', '-'])

    tx_table = Table(tx_rows, colWidths=[70, 180, 100, 60, 110])
    tx_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ]))
    elements.append(tx_table)

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"banksense_report_{date.today().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

