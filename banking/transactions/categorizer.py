import re
from typing import Tuple

CATEGORY_RULES = {
    'Salary': {
        'keywords': [
            'salary', 'payroll', 'wages', 'stipend', 'bonus', 'direct dep', 'direct deposit',
            'corp pay', 'earnings', 'monthly salary', 'compensation'
        ],
        'requires_credit': True,
        'weight': 0.95,
    },
    'Rent': {
        'keywords': [
            'rent', 'landlord', 'housing', 'lease', 'apartment', 'realty', 'property mgmt',
            'tenancy', 'society maintenance', 'maintenance charges', 'pg rent'
        ],
        'requires_credit': False,
        'weight': 0.90,
    },
    'Food': {
        'keywords': [
            'swiggy', 'zomato', 'ubereats', 'doordash', 'grubhub', 'restaurant', 'cafe',
            'coffee', 'starbucks', 'dunkin', 'mcdonald', 'burger', 'pizza', 'domino',
            'kfc', 'subway', 'bistro', 'diner', 'bakery', 'supermarket', 'grocery',
            'blinkit', 'zepto', 'instamart', 'bigbasket', 'dmart', 'nature basket',
            'bar & grill', 'kitchen', 'food court', 'tea point', 'dhaba'
        ],
        'requires_credit': False,
        'weight': 0.90,
    },
    'Shopping': {
        'keywords': [
            'amazon', 'flipkart', 'myntra', 'ebay', 'walmart', 'target', 'ikea', 'zara',
            'h&m', 'uniqlo', 'retail', 'clothing', 'apparel', 'electronics', 'apple store',
            'croma', 'reliance digital', 'mall', 'fashion', 'footwear', 'decathlon',
            'nykaa', 'tata cliq', 'ajio', 'meesho'
        ],
        'requires_credit': False,
        'weight': 0.88,
    },
    'Bills': {
        'keywords': [
            'electricity', 'electric', 'power', 'water utility', 'water bill', 'bescom',
            'gas', 'indane', 'hp gas', 'bharat gas', 'broadband', 'wifi', 'internet',
            'airtel', 'jio', 'vodafone', 'vi prepaid', 'mobile recharge', 'dth',
            'tata play', 'utility', 'municipal', 'property tax', 'billdesk'
        ],
        'requires_credit': False,
        'weight': 0.90,
    },
    'Travel': {
        'keywords': [
            'uber', 'ola', 'lyft', 'rapido', 'taxi', 'cab', 'metro', 'subway', 'train',
            'irctc', 'railway', 'flight', 'airline', 'indigo', 'air india', 'spicejet',
            'emirates', 'delta', 'makemytrip', 'goibibo', 'booking.com', 'agoda',
            'hotel', 'resort', 'airbnb', 'petrol', 'fuel', 'diesel', 'shell',
            'hpcl', 'iocl', 'bpcl', 'toll', 'fastag', 'parking'
        ],
        'requires_credit': False,
        'weight': 0.90,
    },
    'Entertainment': {
        'keywords': [
            'netflix', 'spotify', 'hotstar', 'disney', 'amazon prime', 'prime video',
            'hulu', 'apple music', 'youtube premium', 'multiplex', 'cinema', 'pvr',
            'inox', 'cinepolis', 'bookmyshow', 'gaming', 'steam', 'playstation',
            'xbox', 'concert', 'theater', 'audible', 'patreon'
        ],
        'requires_credit': False,
        'weight': 0.92,
    },
    'Healthcare': {
        'keywords': [
            'hospital', 'clinic', 'pharmacy', 'chemist', 'apollo', 'medplus', '1mg',
            'pharmeasy', 'dental', 'doctor', 'physician', 'pathology', 'diagnostics',
            'blood test', 'lab', 'health insurance', 'mediclaim', 'opticals', 'lenskart',
            'therapy', 'counseling'
        ],
        'requires_credit': False,
        'weight': 0.90,
    },
    'ATM withdrawals': {
        'keywords': [
            'atm wdl', 'atm cash', 'cash wdl', 'atm withdrawal', 'nfs cash',
            'atw', 'atm-csh', 'cash disp'
        ],
        'requires_credit': False,
        'weight': 0.98,
    },
    'Investments': {
        'keywords': [
            'zerodha', 'groww', 'upstox', 'mutual fund', 'sip', 'etf', 'stock',
            'shares', 'demat', 'nse', 'bse', 'coin', 'crypto', 'binance', 'coinbase',
            'fixed deposit', 'recurring deposit', 'fd creation', 'ppf', 'nps', 'vanguard'
        ],
        'requires_credit': False,
        'weight': 0.92,
    },
    'Transfers': {
        'keywords': [
            'upi/', 'upi transfer', 'imps', 'neft', 'rtgs', 'transfer to', 'transfer from',
            'fund transfer', 'p2p', 'wire transfer', 'sent to', 'received from', 'venmo',
            'zelle', 'cash app'
        ],
        'requires_credit': False,
        'weight': 0.80,
    },
}


def categorize_transaction(description: str, transaction_type: str = 'DEBIT') -> Tuple[str, float]:
    """
    Categorizes a transaction based on description keywords and transaction type.
    Returns (category_name, confidence_score).
    """
    if not description:
        return 'Other', 0.50

    desc_lower = description.lower()
    tx_type = transaction_type.upper() if transaction_type else 'DEBIT'

    # Check Salary first for Credit transactions
    if tx_type == 'CREDIT':
        for kw in CATEGORY_RULES['Salary']['keywords']:
            if kw in desc_lower:
                return 'Salary', CATEGORY_RULES['Salary']['weight']

    # Match each category rule
    best_category = 'Other'
    highest_score = 0.50

    for cat_name, rules in CATEGORY_RULES.items():
        if rules.get('requires_credit') and tx_type != 'CREDIT':
            continue

        for kw in rules['keywords']:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, desc_lower):
                score = rules['weight']
                if score > highest_score:
                    highest_score = score
                    best_category = cat_name
                    break
            elif kw in desc_lower:
                # Substring match (slightly lower confidence)
                score = rules['weight'] - 0.05
                if score > highest_score:
                    highest_score = score
                    best_category = cat_name

    # If Credit and unclassified, mark as Transfers or Other with reasonable confidence
    if best_category == 'Other' and tx_type == 'CREDIT':
        if any(term in desc_lower for term in ['upi', 'imps', 'neft', 'rtgs', 'deposit', 'cr']):
            return 'Transfers', 0.75

    return best_category, round(highest_score, 2)

