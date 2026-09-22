
def extract_po_data(uploaded_file):
    import fitz
    import streamlit as st

    pdf = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    text = ""

    for page in pdf:
        page_text = page.get_text()
        text += page_text

    st.write("TEXT LENGTH:", len(text))

    if len(text.strip()) == 0:
        st.error("No text extracted from PDF")
    else:
        st.subheader("Extracted PDF Text")
        st.text(text[:3000])

    po_no = _search(
        text,
        r"PO\s*NUMBER\s*([A-Z0-9\/\-\_]+)"
    )

    po_date = _search(
        text,
        r"PO\s*DATE\s*([0-9\.\/\-]+)"
    )

    vendor = ""
    vendor_match = re.search(
        r"M/s\.(.*)",
        text,
        re.IGNORECASE
    )

    if vendor_match:
        vendor = vendor_match.group(1).strip()

    subject = ""
    sub_match = re.search(
        r"SUB:(.*)",
        text,
        re.IGNORECASE
    )

    if sub_match:
        subject = sub_match.group(1).strip()

    amount = ""
    amount_type = ""

    grand = re.search(
        r"GRAND\s+TOTAL.*?([\d,]+\.\d+|[\d,]+)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    subtotal = re.search(
        r"SUB\s+TOTAL.*?([\d,]+\.\d+|[\d,]+)",
        text,
        re.IGNORECASE | re.DOTALL
    )

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
