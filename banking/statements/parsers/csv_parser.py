import csv
import io
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from .base import ParsedTransaction, ParsedStatementResult, clean_amount_str, parse_date_str
from transactions.categorizer import categorize_transaction


def detect_columns(header_row: List[str]) -> Dict[str, Optional[int]]:
    cols: Dict[str, Optional[int]] = {
        'date': None,
        'value_date': None,
        'description': None,
        'ref': None,
        'debit': None,
        'credit': None,
        'amount': None,
        'type': None,
        'balance': None,
    }

    for idx, raw_h in enumerate(header_row):
        h = str(raw_h).strip().lower()
        if not h:
            continue

        if any(term == h or term in h for term in ['value date', 'vdate', 'effective date']):
            if cols['value_date'] is None:
                cols['value_date'] = idx
        elif any(term == h or term in h for term in ['date', 'txn date', 'transaction date', 'posting date']):
            if cols['date'] is None:
                cols['date'] = idx
        elif any(term == h or term in h for term in ['description', 'particulars', 'narration', 'details', 'remark', 'transaction details']):
            if cols['description'] is None:
                cols['description'] = idx
        elif any(term == h or term in h for term in ['ref', 'reference', 'chq', 'cheque', 'utr', 'txn id', 'transaction id']):
            if cols['ref'] is None:
                cols['ref'] = idx
        elif any(term == h or term in h for term in ['debit', 'withdrawal', 'dr amount', 'amount debited', 'dr.']):
            if cols['debit'] is None:
                cols['debit'] = idx
        elif any(term == h or term in h for term in ['credit', 'deposit', 'cr amount', 'amount credited', 'cr.']):
            if cols['credit'] is None:
                cols['credit'] = idx
        elif any(term == h or term in h for term in ['balance', 'closing balance', 'avail balance', 'net balance']):
            if cols['balance'] is None:
                cols['balance'] = idx
        elif any(term == h or term in h for term in ['amount', 'txn amount', 'transaction amount']):
            if cols['amount'] is None:
                cols['amount'] = idx
        elif any(term == h or term in h for term in ['type', 'cr/dr', 'dr/cr', 'd/c']):
            if cols['type'] is None:
                cols['type'] = idx

    return cols


def parse_csv_statement(file_obj) -> ParsedStatementResult:
    # Read text content safely
    if hasattr(file_obj, 'read'):
        content = file_obj.read()
        if isinstance(content, bytes):
            # Try utf-8, fallback to latin-1
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')
        else:
            text = content
    else:
        with open(file_obj, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()

    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return ParsedStatementResult(transactions=[], warnings=["CSV file is empty"])

    # Try csv reader with sniffing delimiter
    sample = "\n".join(lines[:10])
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
        delimiter = dialect.delimiter
    except Exception:
        delimiter = ','

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    all_rows = list(reader)

    # Find the header row (the row that has 'date' and either 'description'/'particulars' or 'amount')
    header_idx = -1
    col_map = None
    for idx, row in enumerate(all_rows[:15]):
        detected = detect_columns(row)
        if detected['date'] is not None and (detected['description'] is not None or detected['amount'] is not None or detected['debit'] is not None):
            header_idx = idx
            col_map = detected
            break

    if header_idx == -1 or col_map is None:
        return ParsedStatementResult(
            transactions=[],
            warnings=["Could not automatically identify column headers in the CSV. Please verify column names."]
        )

    transactions: List[ParsedTransaction] = []
    total_credits = Decimal('0.00')
    total_debits = Decimal('0.00')
    opening_balance: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None

    for row in all_rows[header_idx + 1:]:
        if not row or all(c.strip() == '' for c in row):
            continue

        # Extract date
        date_idx = col_map['date']
        if date_idx is None or date_idx >= len(row):
            continue
        parsed_date = parse_date_str(row[date_idx])
        if not parsed_date:
            continue

        # Value date
        val_date = None
        if col_map['value_date'] is not None and col_map['value_date'] < len(row):
            val_date = parse_date_str(row[col_map['value_date']])

        # Description
        desc = "Transaction"
        if col_map['description'] is not None and col_map['description'] < len(row):
            desc = row[col_map['description']].strip() or "Transaction"

        # Reference
        ref_no = None
        if col_map['ref'] is not None and col_map['ref'] < len(row):
            ref_no = row[col_map['ref']].strip() or None

        # Balance after
        balance_after = None
        if col_map['balance'] is not None and col_map['balance'] < len(row):
            balance_after = clean_amount_str(row[col_map['balance']])

        # Determine type & amount
        tx_type = None
        amount = None

        # Check separate debit/credit columns
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
                # Check type column or minus sign
                if col_map['type'] is not None and col_map['type'] < len(row):
                    t_val = row[col_map['type']].strip().lower()
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

    # Sort transactions by date ascending for reconciliation
    transactions.sort(key=lambda t: t.date)

    if transactions:
        # If balance after was present
        first_b = transactions[0].balance_after
        last_b = transactions[-1].balance_after
        if first_b is not None:
            # Reconstruct opening balance: first balance_after - (+first_amt if credit else -first_amt)
            if transactions[0].transaction_type == 'CREDIT':
                opening_balance = first_b - transactions[0].amount
            else:
                opening_balance = first_b + transactions[0].amount
        if last_b is not None:
            closing_balance = last_b

    # Reconciliation
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

