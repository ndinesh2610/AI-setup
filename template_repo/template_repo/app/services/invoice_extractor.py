import re
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image


def extract_invoice(path: str) -> dict:
    file = Path(path)

    if file.suffix.lower() == ".pdf":
        pages = convert_from_path(str(file))
        text = "\n".join(pytesseract.image_to_string(p) for p in pages)
    else:
        text = pytesseract.image_to_string(Image.open(file))

    def find(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def amount(pattern):
        value = find(pattern)
        return float(value.replace(",", "")) if value else None

    return {
        "invoice_number": find(r"Invoice no:\s*(\S+)"),
        "date": find(r"Date:\s*(\d{4}-\d{2}-\d{2})"),
        "due_date": find(r"Due:\s*(\d{4}-\d{2}-\d{2})"),
        "bill_to": find(r"Bill to:\s*(.+)"),
        "subtotal": amount(r"Subtotal:?\s*([\d,]+\.\d{2})"),
        "tax": amount(r"Tax\s*[\d.]*%?:?\s*([\d,]+\.\d{2})"),
        "total_due": amount(r"Total due:?\s*([\d,]+\.\d{2})"),
    }
