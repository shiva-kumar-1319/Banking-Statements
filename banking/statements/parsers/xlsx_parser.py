import io
from decimal import Decimal
from typing import List, Optional
import openpyxl
from .base import ParsedTransaction, ParsedStatementResult, clean_amount_str, parse_date_str
from .csv_parser import detect_columns
from transactions.categorizer import categorize_transaction


def parse_xlsx_statement(file_obj) -> ParsedStatementResult:
    try:
        if hasattr(file_obj, 'read'):
            content = file_obj.read()
            wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
        else:
            wb = openpyxl.load_workbook(file_obj, data_only=True)
    except Exception as e:
        return ParsedStatementResult(
            transactions=[],
            warnings=[f"Failed to read Excel workbook: {str(e)}"]
        )

    sheet = wb.active
    if not sheet:
        return ParsedStatementResult(transactions=[], warnings=["No active sheet in workbook"])

    # Convert sheet rows to string/value rows
    all_rows = []
    for row in sheet.iter_rows(values_only=True):
        row_list = ["" if cell is None else cell for cell in row]
        if any(c != "" for c in row_list):
            all_rows.append(row_list)

    if not all_rows:
        return ParsedStatementResult(transactions=[], warnings=["Excel sheet is empty"])

    header_idx = -1
    col_map = None
    for idx, row in enumerate(all_rows[:20]):
        str_row = [str(c) for c in row]
        detected = detect_columns(str_row)
        if detected['date'] is not None and (detected['description'] is not None or detected['amount'] is not None or detected['debit'] is not None):
            header_idx = idx
            col_map = detected
            break

    if header_idx == -1 or col_map is None:
        return ParsedStatementResult(
            transactions=[],
            warnings=["Could not automatically find header row in Excel sheet."]
        )

    transactions: List[ParsedTransaction] = []
    total_credits = Decimal('0.00')
    total_debits = Decimal('0.00')
    opening_balance: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None

    for row in all_rows[header_idx + 1:]:
        if not row:
            continue

        date_idx = col_map['date']
        if date_idx is None or date_idx >= len(row):
            continue
        parsed_date = parse_date_str(row[date_idx])
        if not parsed_date:
            continue

        val_date = None
        if col_map['value_date'] is not None and col_map['value_date'] < len(row):
            val_date = parse_date_str(row[col_map['value_date']])

        desc = "Transaction"
        if col_map['description'] is not None and col_map['description'] < len(row):
            desc = str(row[col_map['description']]).strip() or "Transaction"

        ref_no = None
        if col_map['ref'] is not None and col_map['ref'] < len(row):
            ref_no = str(row[col_map['ref']]).strip() or None

        balance_after = None
        if col_map['balance'] is not None and col_map['balance'] < len(row):
            balance_after = clean_amount_str(row[col_map['balance']])

        tx_type = None
        amount = None

        debit_val = clean_amount_str(row[col_map['debit']]) if col_map['debit'] is not None and col_map['debit'] < len(row) else None
        credit_val = clean_amount_str(row[col_map['credit']]) if col_map['credit'] is not None and col_map['credit'] < len(row) else None

        if debit_val and debit_val > Decimal('0.00'):
            tx_type = 'DEBIT'
            amount = debit_val
        elif credit_val and credit_val > Decimal('0.00'):
            tx_type = 'CREDIT'
            amount = credit_val
        elif col_map['amount'] is not None and col_map['amount'] < len(row):
            raw_amt = row[col_map['amount']]
            cleaned = clean_amount_str(raw_amt)
            if cleaned is not None:
                amount = cleaned
                if col_map['type'] is not None and col_map['type'] < len(row):
                    t_val = str(row[col_map['type']]).strip().lower()
                    if 'cr' in t_val or 'credit' in t_val or 'dep' in t_val:
                        tx_type = 'CREDIT'
                    else:
                        tx_type = 'DEBIT'
                else:
                    if '-' in str(raw_amt) or '(' in str(raw_amt):
                        tx_type = 'DEBIT'
                    else:
                        tx_type = 'CREDIT'

        if not amount or amount <= Decimal('0.00') or not tx_type:
            continue

        if tx_type == 'CREDIT':
            total_credits += amount
        else:
            total_debits += amount

        category, confidence = categorize_transaction(desc, tx_type)

        tx = ParsedTransaction(
            date=parsed_date,
            value_date=val_date,
            description=desc,
            reference_number=ref_no,
            transaction_type=tx_type,
            amount=amount,
            balance_after=balance_after,
            category=category,
            confidence=confidence,
        )
        transactions.append(tx)

    transactions.sort(key=lambda t: t.date)

    if transactions:
        first_b = transactions[0].balance_after
        last_b = transactions[-1].balance_after
        if first_b is not None:
            if transactions[0].transaction_type == 'CREDIT':
                opening_balance = first_b - transactions[0].amount
            else:
                opening_balance = first_b + transactions[0].amount
        if last_b is not None:
            closing_balance = last_b

    reconciled_status = 'UNVERIFIED'
    recon_diff = Decimal('0.00')
    if opening_balance is not None and closing_balance is not None:
        calc_closing = opening_balance + total_credits - total_debits
        recon_diff = abs(calc_closing - closing_balance)
        if recon_diff < Decimal('0.05'):
            reconciled_status = 'RECONCILED'
        else:
            reconciled_status = 'DISCREPANCY'

    return ParsedStatementResult(
        transactions=transactions,
        opening_balance=opening_balance,
        closing_balance=closing_balance,
        total_credits=total_credits,
        total_debits=total_debits,
        reconciliation_status=reconciled_status,
        reconciliation_difference=recon_diff,
    )

