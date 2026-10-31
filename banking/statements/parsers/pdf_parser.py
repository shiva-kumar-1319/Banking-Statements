import io
import re
from decimal import Decimal
from typing import List, Optional
import pdfplumber
from .base import ParsedTransaction, ParsedStatementResult, clean_amount_str, parse_date_str
from .csv_parser import detect_columns
from transactions.categorizer import categorize_transaction


def extract_balances_from_text(full_text: str) -> (Optional[Decimal], Optional[Decimal]):
    opening_bal = None
    closing_bal = None

    open_match = re.search(r'(?:opening\s*balance|open\s*bal|b/f|balance\s*brought\s*forward)[\s:]*([₹$€£\s0-9,\.\-]+)', full_text, re.IGNORECASE)
    if open_match:
        opening_bal = clean_amount_str(open_match.group(1))

    close_match = re.search(r'(?:closing\s*balance|close\s*bal|c/f|balance\s*carried\s*forward|ending\s*balance)[\s:]*([₹$€£\s0-9,\.\-]+)', full_text, re.IGNORECASE)
    if close_match:
        closing_bal = clean_amount_str(close_match.group(1))

    return opening_bal, closing_bal


def parse_pdf_statement(file_obj) -> ParsedStatementResult:
    warnings = []
    transactions: List[ParsedTransaction] = []
    total_credits = Decimal('0.00')
    total_debits = Decimal('0.00')
    full_text = ""

    try:
        if hasattr(file_obj, 'read'):
            content = file_obj.read()
            pdf = pdfplumber.open(io.BytesIO(content))
        else:
            pdf = pdfplumber.open(file_obj)
    except Exception as e:
        return ParsedStatementResult(
            transactions=[],
            warnings=[f"Failed to open PDF statement: {str(e)}"]
        )

    # Strategy 1: Table extraction across pages
    extracted_any_table = False

    with pdf:
        for page_num, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            full_text += "\n" + page_text

            tables = page.extract_tables()
            if not tables:
                continue

            for table in tables:
                if not table or len(table) < 2:
                    continue

                # Find header row
                header_idx = -1
                col_map = None
                for idx, row in enumerate(table[:10]):
                    str_row = [str(c or '').strip() for c in row]
                    detected = detect_columns(str_row)
                    if detected['date'] is not None and (detected['description'] is not None or detected['amount'] is not None or detected['debit'] is not None):
                        header_idx = idx
                        col_map = detected
                        extracted_any_table = True
                        break

                if header_idx != -1 and col_map is not None:
                    for row in table[header_idx + 1:]:
                        if not row or all(not str(c or '').strip() for c in row):
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
                            desc = str(row[col_map['description']] or '').strip().replace('\n', ' ') or "Transaction"

                        ref_no = None
                        if col_map['ref'] is not None and col_map['ref'] < len(row):
                            ref_no = str(row[col_map['ref']] or '').strip() or None

                        balance_after = None
                        if col_map['balance'] is not None and col_map['balance'] < len(row):
                            balance_after = clean_amount_str(row[col_map['balance']])

                        debit_val = clean_amount_str(row[col_map['debit']]) if col_map['debit'] is not None and col_map['debit'] < len(row) else None
                        credit_val = clean_amount_str(row[col_map['credit']]) if col_map['credit'] is not None and col_map['credit'] < len(row) else None

                        tx_type = None
                        amount = None

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
                                    t_val = str(row[col_map['type']] or '').strip().lower()
                                    if 'cr' in t_val or 'credit' in t_val:
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

    # Strategy 2: If table extraction failed or returned few transactions, parse free text lines
    if len(transactions) == 0:
        lines = [line.strip() for line in full_text.splitlines() if line.strip()]
        line_pattern = re.compile(
            r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}\s+[A-Za-z]{3}\s+\d{2,4})\s+(.+?)\s+([₹$€£\s\d,]+\.\d{2})\s*(CR|DR|Cr|Dr)?\s*([₹$€£\s\d,]+\.\d{2})?'
        )

        for line in lines:
            m = line_pattern.search(line)
            if not m:
                continue

            raw_date, raw_desc, raw_amt, raw_type, raw_bal = m.groups()
            parsed_date = parse_date_str(raw_date)
            if not parsed_date:
                continue

            amount = clean_amount_str(raw_amt)
            if not amount or amount <= Decimal('0.00'):
                continue

            balance_after = clean_amount_str(raw_bal) if raw_bal else None

            # Determine type
            tx_type = 'DEBIT'
            if raw_type:
                if 'cr' in raw_type.lower():
                    tx_type = 'CREDIT'
            elif 'credit' in line.lower() or 'deposit' in line.lower() or 'salary' in line.lower():
                tx_type = 'CREDIT'

            if tx_type == 'CREDIT':
                total_credits += amount
            else:
                total_debits += amount

            category, confidence = categorize_transaction(raw_desc.strip(), tx_type)

            tx = ParsedTransaction(
                date=parsed_date,
                description=raw_desc.strip() or "Transaction",
                transaction_type=tx_type,
                amount=amount,
                balance_after=balance_after,
                category=category,
                confidence=confidence,
            )
            transactions.append(tx)

    # Balance extraction from text
    opening_balance, closing_balance = extract_balances_from_text(full_text)

    transactions.sort(key=lambda t: t.date)

    if transactions:
        if opening_balance is None and transactions[0].balance_after is not None:
            if transactions[0].transaction_type == 'CREDIT':
                opening_balance = transactions[0].balance_after - transactions[0].amount
            else:
                opening_balance = transactions[0].balance_after + transactions[0].amount
        if closing_balance is None and transactions[-1].balance_after is not None:
            closing_balance = transactions[-1].balance_after

    reconciled_status = 'UNVERIFIED'
    recon_diff = Decimal('0.00')
    if opening_balance is not None and closing_balance is not None:
        calc_closing = opening_balance + total_credits - total_debits
        recon_diff = abs(calc_closing - closing_balance)
        if recon_diff < Decimal('0.05'):
            reconciled_status = 'RECONCILED'
        else:
            reconciled_status = 'DISCREPANCY'

    if not transactions:
        warnings.append("No transactions could be extracted from this PDF statement. Please ensure it is a valid bank statement containing readable text or tables.")

    return ParsedStatementResult(
        transactions=transactions,
        opening_balance=opening_balance,
        closing_balance=closing_balance,
        total_credits=total_credits,
        total_debits=total_debits,
        reconciliation_status=reconciled_status,
        reconciliation_difference=recon_diff,
        warnings=warnings,
    )

