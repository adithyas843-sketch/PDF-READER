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
        text += "\n"
        text += pytesseract.image_to_string(img)

    # Debug OCR text
    with st.expander(f"OCR Text - {uploaded_file.name}"):
        st.text(text[:15000])

    # --------------------------------------------------
    # Vendor
    # --------------------------------------------------

    vendor = ""

    vendor_patterns = [
        r"M/s\.?\s*([^\n\r]+)",
        r"M\/s\.?\s*([^\n\r]+)"
    ]

    for pattern in vendor_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            vendor = clean_text(match.group(1))
            break

    # --------------------------------------------------
    # Description
    # --------------------------------------------------

    description = ""

    description_patterns = [

        r"WORK\s+ORDER\s+FOR\s+(.*?)\s+AT\s+GOLDFINCH",

        r"PURCHASE\s+ORDER\s+FOR\s+(.*?)\s+AT\s+GOLDFINCH",

        r"WORK\s+ORDER\s+FOR\s+(.*?)\s+\(",

        r"PURCHASE\s+ORDER\s+FOR\s+(.*?)\s+\(",

        r"SUB:\s*(.*?)\s+AT\s+GOLDFINCH"
    ]

    for pattern in description_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:

            description = clean_text(
                match.group(1)
            )

            break

    # --------------------------------------------------
    # Amount Excluding GST
    # --------------------------------------------------

    amount = ""

    amount_patterns = [

        r"TOTAL\s*\(EXCLUDING\s*GST\)\s*[:\-]?\s*([\d,]+\.\d{2})",

        r"TOTAL\s*\(EXCLUDING\s*GST\)\s*[:\-]?\s*([\d,]+)",

        r"SUB\s*TOTAL\s*[:\-]?\s*([\d,]+\.\d{2})",

        r"SUB\s*TOTAL\s*[:\-]?\s*([\d,]+)",

        r"TOTAL\s*[:\-]?\s*([\d,]+\.\d{2}).{0,100}GST",

        r"TOTAL\s*[:\-]?\s*([\d,]+).{0,100}GST"
    ]

    for pattern in amount_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:

            amount = match.group(1)
            break

    # --------------------------------------------------
    # Fallback Amount
    # --------------------------------------------------

    if amount == "":

        lines = text.splitlines()

        for i, line in enumerate(lines):

            if "GST" in line.upper():

                for j in range(max(0, i - 5), i):

                    nums = re.findall(
                        r"[\d,]+\.\d{2}|[\d,]+",
                        lines[j]
                    )

                    if nums:

                        amount = nums[-1]
                        break

                if amount:
                    break

    # --------------------------------------------------
    # Clean Amount
    # --------------------------------------------------

    amount = amount.replace(" ", "")

    # --------------------------------------------------
    # Return
    # --------------------------------------------------

    return {
        "Material Vendor": vendor,
        "Description (Scope of Work in Brief)": description,
        "Amount Excl GST": amount,
        "File Name": uploaded_file.name
    }
