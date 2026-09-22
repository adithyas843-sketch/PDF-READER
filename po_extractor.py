
import re
from pdf2image import convert_from_bytes
import pytesseract

def extract_po_data(uploaded_file):

    images = convert_from_bytes(uploaded_file.read(), dpi=300)

    text = ""
    for img in images:
        text += "\n" + pytesseract.image_to_string(img)

    vendor = ""
    po_no = ""
    po_date = ""
    subject = ""
    amount = ""

    m = re.search(r'ANMOL TRADING COMPANY|M/s\.?\s*(.+)', text, re.I)
    if m:
        vendor = m.group(0).strip()

    po_patterns = [
        r'GFG/\d{4}-\d{2}/[A-Z&\-]+-\d+',
        r'PO\s*NUMBER.*?([A-Z0-9/\-]+)'
    ]

    for p in po_patterns:
        m = re.search(p, text, re.I)
        if m:
            po_no = m.group(0)
            break

    m = re.search(
    r'PO\s*DATE\s*[:\-]?\s*(\d{2}[./-]\d{2}[./-]\d{4})',
    text,
    re.I
)

if m:
    po_date = m.group(1)
    m = re.search(r'PURCHASE ORDER FOR(.*)', text, re.I)
    if m:
        subject = m.group(1).strip()[:150]

    amounts = re.findall(r'[\d,]+\.\d{2}|[\d,]+', text)
    if amounts:
        amount = max(amounts, key=lambda x: len(x.replace(",","")))

    return {
        "Material Vendor": vendor,
        "PO Date": po_date,
        "PO No": po_no,
        "Description (Scope of Work in Brief)": subject,
        "Amount Total": amount,
        "File Name": uploaded_file.name
    }
