import re
import fitz
from pdf2image import convert_from_bytes
import pytesseract
import streamlit as st


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_text_from_pdf(uploaded_file):

    pdf_bytes = uploaded_file.read()

    # Try direct PDF text extraction first
    try:
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

        text = ""

        for page in pdf:
            text += page.get_text()

        if len(text.strip()) > 200:
            return text

    except Exception:
        pass

    # OCR fallback
    images = convert_from_bytes(pdf_bytes, dpi=300)

    text = ""

    for img in images:
        text += "\n"
        text += pytesseract.image_to_string(img)

    return text


def extract_vendor(text):

    patterns = [
        r"M/s\.?\s*([^\n\r]+)",
        r"M\/s\.?\s*([^\n\r]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            vendor = clean_text(match.group(1))

            vendor = vendor.replace("PO NUMBER", "")
            vendor = vendor.replace("PO NO", "")

            return vendor.strip(" ,:-")

    return ""


def extract_description(text):

    patterns = [

        r"PURCHASE\s+ORDER\s+FOR\s+(.*?)\s+TO\s+GOLDFINCH",

        r"WORK\s+ORDER\s+FOR\s+(.*?)\s+AT\s+GOLDFINCH",

        r"WORK\s+ORDER\s+FOR\s+(.*?)\s+TO\s+GOLDFINCH",

        r"SUB:\s*(.*?)\s+TO\s+GOLDFINCH"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            return clean_text(match.group(1))

    return ""


def extract_amount(text):

    # Show total-related lines for debugging
    st.write("### TOTAL DEBUG")

    for line in text.splitlines():

        if (
            "TOTAL" in line.upper()
            or "GST" in line.upper()
        ):
            st.write(line)

    # Convert newlines to spaces
    text_flat = text.replace("\n", " ")

    patterns = [

        r"TOTAL\s*\(EXCLUDING\s*GST\)\s*[:\-]?\s*([\d,]+\.\d{2})",
        r"TOTAL\s*\(EXCLUDING\s*GST\)\s*[:\-]?\s*([\d,]+)",

        r"SUB\s*TOTAL\s*[:\-]?\s*([\d,]+\.\d{2})",
        r"SUB\s*TOTAL\s*[:\-]?\s*([\d,]+)",

        r"SUBTOTAL\s*[:\-]?\s*([\d,]+\.\d{2})",
        r"SUBTOTAL\s*[:\-]?\s*([\d,]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text_flat,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return ""


def extract_po_data(uploaded_file):

    text = extract_text_from_pdf(uploaded_file)

    with st.expander(f"PDF TEXT - {uploaded_file.name}"):

        st.text(text[:15000])

    vendor = extract_vendor(text)

    description = extract_description(text)

    amount = extract_amount(text)

    return {
        "Material Vendor": vendor,
        "Description (Scope of Work in Brief)": description,
        "Amount Excl GST": amount,
        "File Name": uploaded_file.name
    }
