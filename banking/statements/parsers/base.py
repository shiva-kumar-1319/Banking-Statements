import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class ParsedTransaction:
    date: date
    description: str
    transaction_type: str  # 'DEBIT' or 'CREDIT'
    amount: Decimal
    value_date: Optional[date] = None
    reference_number: Optional[str] = None
    balance_after: Optional[Decimal] = None
    category: str = 'Other'
    confidence: float = 1.0
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'date': self.date.isoformat(),
            'value_date': self.value_date.isoformat() if self.value_date else None,
            'description': self.description,
            'reference_number': self.reference_number,
            'transaction_type': self.transaction_type,
            'amount': str(self.amount),
            'balance_after': str(self.balance_after) if self.balance_after is not None else None,
            'category': self.category,
            'confidence': self.confidence,
        }


@dataclass
class ParsedStatementResult:
    transactions: List[ParsedTransaction]
    opening_balance: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None
    total_credits: Decimal = Decimal('0.00')
    total_debits: Decimal = Decimal('0.00')
    reconciliation_status: str = 'UNVERIFIED'
    reconciliation_difference: Decimal = Decimal('0.00')
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'transactions': [t.to_dict() for t in self.transactions],
            'opening_balance': str(self.opening_balance) if self.opening_balance is not None else None,
            'closing_balance': str(self.closing_balance) if self.closing_balance is not None else None,
            'total_credits': str(self.total_credits),
            'total_debits': str(self.total_debits),
            'total_count': len(self.transactions),
            'reconciliation_status': self.reconciliation_status,
            'reconciliation_difference': str(self.reconciliation_difference),
            'warnings': self.warnings,
        }


def clean_amount_str(raw: Any) -> Optional[Decimal]:
    """Cleans a raw amount representation into a positive Decimal, or None if invalid."""
    if raw is None or raw == '':
        return None
    if isinstance(raw, (int, float)):
        return Decimal(str(abs(raw)))
    if isinstance(raw, Decimal):
        return abs(raw)

    s = str(raw).strip()
    if not s or s in ['-', '--', 'N/A', 'nil', 'null']:
        return None

    # Strip currency symbols and whitespace
    s = re.sub(r'[$₹€£RsINR\s]', '', s, flags=re.IGNORECASE)

    # Check for negative in parentheses e.g. (123.45) or leading minus
    is_negative = False
    if s.startswith('(') and s.endswith(')'):
        is_negative = True
        s = s[1:-1].strip()
    elif s.startswith('-') or s.endswith('-'):
        is_negative = True
        s = s.replace('-', '').strip()

    # Handle commas
    s = s.replace(',', '')

    try:
        val = Decimal(s)
        return abs(val)
    except (InvalidOperation, ValueError):
        return None


DATE_FORMATS = [
    '%Y-%m-%d',
    '%d-%m-%Y',
    '%d/%m/%Y',
    '%m/%d/%Y',
    '%d.%m.%Y',
    '%d %b %Y',
    '%d %B %Y',
    '%b %d, %Y',
    '%B %d, %Y',
    '%d-%b-%Y',
    '%d-%b-%y',
    '%d/%m/%y',
    '%y-%m-%d',
]


def parse_date_str(raw: Any) -> Optional[date]:
    """Tries parsing various date formats into a datetime.date object."""
    if raw is None:
        return None
    if isinstance(raw, (datetime, date)):
        return raw if isinstance(raw, date) else raw.date()

    s = str(raw).strip()
    if not s:
        return None

    # Remove extra spaces and time components if present
    s = s.split('T')[0].split(' ')[0] if 'T' in s else s

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue

    # Try matching regex for e.g. "24 May 2026"
    m = re.search(r'(\d{1,2})[\s\-\/\.]?([A-Za-z]{3,9})[\s\-\/\.]?(\d{2,4})', str(raw))
    if m:
        combined = f"{m.group(1)} {m.group(2)} {m.group(3)}"
        for fmt in ['%d %b %Y', '%d %B %Y', '%d %b %y']:
            try:
                return datetime.strptime(combined, fmt).date()
            except ValueError:
                pass

    return None

