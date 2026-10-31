import os
from .base import ParsedStatementResult
from .csv_parser import parse_csv_statement
from .xlsx_parser import parse_xlsx_statement
from .pdf_parser import parse_pdf_statement


def extract_statement(file_obj, filename: str) -> ParsedStatementResult:
    ext = os.path.splitext(filename)[1].lower()

    if ext == '.csv':
        return parse_csv_statement(file_obj)
    elif ext in ['.xlsx', '.xls']:
        return parse_xlsx_statement(file_obj)
    elif ext == '.pdf':
        return parse_pdf_statement(file_obj)
    else:
        return ParsedStatementResult(
            transactions=[],
            warnings=[f"Unsupported file format '{ext}'. Supported formats: .pdf, .csv, .xlsx"]
        )

