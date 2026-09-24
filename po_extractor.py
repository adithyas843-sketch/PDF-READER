import re
import fitz
from pdf2image import convert_from_bytes
import pytesseract
import streamlit as st


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_text_from_pdf(uploaded_file):

    pdf_bytes = uploaded_file.read()

    # First try direct PDF text extraction
    try:
        pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

        text = ""

        for page in pdf:
            text += page.get_text()

        if len(text.strip()) > 200:
            return text

    except Exception:
        pass

    # Fallback OCR
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

        m = re.search(pattern, text, re.IGNORECASE)

        if m:

            vendor = clean_text(m.group(1))

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

        m = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        if m:
            return clean_text(m.group(1))

    return ""


def extract_amount(text):

    # Case 1
    patterns = [

        r"TOTAL\s*\(EXCLUDING\s*GST\)\s*[:\-]?\s*([\d,]+)",

        r"SUB\s*TOTAL\s*[:\-]?\s*([\d,]+)",

        r"SUBTOTAL\s*[:\-]?\s*([\d,]+)"
    ]

    for pattern in patterns:

        m = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if m:
            return m.group(1)

    # Case 2
    lines = text.splitlines()

    for i, line in enumerate(lines):

        if "GST" in line.upper():

            for j in range(i - 1, max(-1, i - 8), -1):

                nums = re.findall(
                    r"\d[\d,]*",
                    lines[j]
                )

                if nums:
                    return nums[-1]

    return ""


def extract_po_data(uploaded_file):

    text = extract_text_from_pdf(uploaded_file)

    with st.expander(f"OCR/Text Output - {uploaded_file.name}"):

        st.text(text[:10000])

    vendor = extract_vendor(text)

    description = extract_description(text)

    amount = extract_amount(text)

    return {
        "Material Vendor": vendor,
        "Description (Scope of Work in Brief)": description,
        "Amount Excl GST": amount,
        "File Name": uploaded_file.name
    }
