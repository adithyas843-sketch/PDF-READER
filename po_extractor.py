import re
from pdf2image import convert_from_bytes
import pytesseract
import streamlit as st


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_po_data(uploaded_file):

    images = convert_from_bytes(
        uploaded_file.read(),
        dpi=300
    )

    text = ""

    for img in images:
        page_text = pytesseract.image_to_string(img)
        text += "\n" + page_text

    # DEBUG - REMOVE LATER
    with st.expander(f"OCR Text - {uploaded_file.name}"):
        st.text(text[:10000])

    text_clean = clean_text(text)

    vendor = ""
    po_no = ""
    po_date = ""
    description = ""
    amount = ""

    # --------------------------------------------------
    # VENDOR
    # --------------------------------------------------

    vendor_patterns = [
        r"M/s\.?\s*([A-Z0-9 &.,\-]+)",
        r"TO\s*M/s\.?\s*([A-Z0-9 &.,\-]+)"
    ]

    for pattern in vendor_patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            vendor = match.group(1).strip()
            break

    # --------------------------------------------------
    # PO NUMBER
    # --------------------------------------------------

    po_patterns = [
        r"GFG/\d{4}-\d{2}/[A-Z&\-]+-\d+",
        r"PO\s*NUMBER\s*([A-Z0-9/\-&]+)"
    ]

    for pattern in po_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            if match.groups():
                po_no = match.group(1)
            else:
                po_no = match.group(0)

            break

    # --------------------------------------------------
    # PO DATE
    # --------------------------------------------------

    date_patterns = [
        r"PO\s*DATE\s*[:\-]?\s*(\d{2}[./-]\d{2}[./-]\d{4})",
        r"(\d{2}[./-]\d{2}[./-]\d{4})"
    ]

    for pattern in date_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            po_date = match.group(1)
            break

    # --------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------

    desc_patterns = [
        r"SUB:\s*(.*?)Dear",
        r"SUB:\s*(.*?)(?:\n|\r)",
        r"PURCHASE ORDER FOR\s*(.*?)(?:\n|\r)"
    ]

    for pattern in desc_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            description = clean_text(match.group(1))
            break

    # --------------------------------------------------
    # GRAND TOTAL
    # --------------------------------------------------

    grand_patterns = [
        r"GRAND\s*TOTAL\s*([\d,]+\.\d{2})",
        r"GRAND\s*TOTAL\s*([\d,]+)",
        r"SUB\s*TOTAL\s*([\d,]+\.\d{2})",
        r"SUB\s*TOTAL\s*([\d,]+)"
    ]

    for pattern in grand_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            amount = match.group(1)
            break

    # --------------------------------------------------
    # FALLBACK AMOUNT
    # --------------------------------------------------

    if amount == "":

        amounts = re.findall(
            r"\b\d{1,3}(?:,\d{3})+\b",
            text
        )

        if amounts:
            amount = amounts[-1]

    # --------------------------------------------------
    # RETURN
    # --------------------------------------------------

    return {
        "Material Vendor": vendor,
        "PO Date": po_date,
        "PO No": po_no,
        "Description (Scope of Work in Brief)": description,
        "Amount Total": amount,
        "File Name": uploaded_file.name
    }
