import os
import csv
from datetime import date
from decimal import Decimal
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample_statements')
os.makedirs(SAMPLES_DIR, exist_ok=True)

CSV_FILE = os.path.join(SAMPLES_DIR, 'sample_bank_statement.csv')
XLSX_FILE = os.path.join(SAMPLES_DIR, 'sample_salary_account.xlsx')
PDF_FILE = os.path.join(SAMPLES_DIR, 'sample_premium_statement.pdf')

sample_transactions = [
    ("2026-05-01", "Opening Balance", "", "", "", "50000.00"),
    ("2026-05-02", "ACH Direct Dep CORP PAYROLL SALARY", "SAL982103", "", "75000.00", "125000.00"),
    ("2026-05-03", "Transfer to Landlord APARTMENT RENT", "TXN102938", "25000.00", "", "100000.00"),
    ("2026-05-05", "SWIGGY BANGALORE IN FOOD ORDER", "SWG88291", "1240.00", "", "98760.00"),
    ("2026-05-08", "AMAZON RETAIL INDIA PVT LTD ELECTRONICS", "AMZ44921", "6499.00", "", "92261.00"),
    ("2026-05-10", "BESCOM ELECTRICITY UTILITY BILL", "ELE99102", "2350.00", "", "89911.00"),
    ("2026-05-12", "UBER INDIA RIDES TRIP REF 8821", "UBR11029", "540.00", "", "89371.00"),
    ("2026-05-15", "NETFLIX ENTERTAINMENT MONTHLY SUB", "NFLX992", "649.00", "", "88722.00"),
    ("2026-05-18", "ZERODHA BROKING MUTUAL FUND SIP", "ZER99120", "15000.00", "", "73722.00"),
    ("2026-05-20", "APOLLO PHARMACY HEALTHCARE MEDICINES", "APL3391", "1850.00", "", "71872.00"),
    ("2026-05-22", "ATM CASH WDL NFS SBI KORAMANGALA", "ATM1002", "5000.00", "", "66872.00"),
    ("2026-05-25", "ZOMATO RESTAURANT DINING EXPENSE", "ZOM4491", "1480.00", "", "65392.00"),
    ("2026-05-28", "FREELANCE DESIGN CLIENT PAYMENT", "CLI88201", "", "18000.00", "83392.00"),
    ("2026-05-30", "AIRTEL BROADBAND FIBER BILL", "ART0029", "1199.00", "", "82193.00"),
]

def make_csv():
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Narration", "Chq/Ref No", "Withdrawal (Dr)", "Deposit (Cr)", "Closing Balance"])
        for row in sample_transactions[1:]:  # skip opening balance row in table
            writer.writerow(row)
    print(f"Created CSV: {CSV_FILE}")

def make_xlsx():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Statement"
    headers = ["Transaction Date", "Particulars", "Reference No", "Debit", "Credit", "Balance"]
    ws.append(headers)
    for row in sample_transactions[1:]:
        ws.append([
            row[0],
            row[1],
            row[2],
            float(row[3]) if row[3] else None,
            float(row[4]) if row[4] else None,
            float(row[5]) if row[5] else None,
        ])
    wb.save(XLSX_FILE)
    print(f"Created XLSX: {XLSX_FILE}")

def make_pdf():
    doc = SimpleDocTemplate(PDF_FILE, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#1e293b'))
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#475569'))

    elements = [
        Paragraph("<b>HDFC BANK — ACCOUNT STATEMENT</b>", title_style),
        Paragraph("Customer Name: Aarav Sharma &nbsp;|&nbsp; Account: •••• 1024 &nbsp;|&nbsp; Currency: INR", meta_style),
        Paragraph("Opening Balance: 50,000.00 &nbsp;|&nbsp; Closing Balance: 82,193.00 &nbsp;|&nbsp; Period: 01-May-2026 to 31-May-2026", meta_style),
        Spacer(1, 14)
    ]

    table_data = [["Date", "Description", "Ref No", "Debit", "Credit", "Balance"]]
    for row in sample_transactions[1:]:
        table_data.append([
            row[0],
            row[1][:30],
            row[2],
            row[3] or "-",
            row[4] or "-",
            row[5],
        ])

    table = Table(table_data, colWidths=[65, 195, 75, 65, 65, 75])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)
    doc.build(elements)
    print(f"Created PDF: {PDF_FILE}")

if __name__ == '__main__':
    make_csv()
    make_xlsx()
    make_pdf()

