
import re
import fitz

def extract_po_data(uploaded_file):
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    text = ""
    for page in pdf:
        text += page.get_text()
        print("==== PDF TEXT START ====")
print(text[:3000])
print("==== PDF TEXT END ====")

    po_no = _search(text, r"PO\s*NUMBER\s*([A-Z0-9\/\-\_]+)")
    po_date = _search(text, r"PO\s*DATE\s*([0-9\.\/\-]+)")

    vendor = ""
    vendor_match = re.search(r"M/s\.(.*)", text, re.IGNORECASE)
    if vendor_match:
        vendor = vendor_match.group(1).strip()

    subject = ""
    sub_match = re.search(r"SUB:(.*)", text, re.IGNORECASE)
    if sub_match:
        subject = sub_match.group(1).strip()

    amount = ""
    amount_type = ""

    grand = re.search(r"GRAND\s+TOTAL.*?([\d,]+\.\d+|[\d,]+)", text, re.IGNORECASE | re.DOTALL)
    subtotal = re.search(r"SUB\s+TOTAL.*?([\d,]+\.\d+|[\d,]+)", text, re.IGNORECASE | re.DOTALL)

    if grand:
        amount = grand.group(1)
        amount_type = "Including GST"
    elif subtotal:
        amount = subtotal.group(1)
        amount_type = "Excluding GST"

    return {
        "Material Vendor": vendor,
        "PO Date": po_date,
        "PO No": po_no,
        "Description (Scope of Work in Brief)": subject,
        "Amount Total": amount,
        "Amount Type": amount_type,
    }

def _search(text, pattern):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else ""
