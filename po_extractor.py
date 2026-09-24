import re
import fitz
from pdf2image import convert_from_bytes
import pytesseract
import streamlit as st


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_text_from_pdf(uploaded_file):

    pdf_bytes = uploaded_file.read()

    # First try direct text extraction
    try:

        pdf = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        text = ""

        for page in pdf:
            text += page.get_text()

        if len(text.strip()) > 200:
            return text

    except Exception:
        pass

    # OCR fallback
    images = convert_from_bytes(
        pdf_bytes,
        dpi=300
    )

    text = ""

    for img in images:
        text += "\n"
        text += pytesseract.image_to_string(img)

    return text


def extract_vendor(text):

    lines = text.splitlines()

    for i, line in enumerate(lines):

        if (
            "M/s" in line
            or "M/S" in line
            or "M/s." in line
        ):

            # Same line
            match = re.search(
                r"M/s\.?\s*(.*)",
                line,
                re.IGNORECASE
            )

            if match:

                vendor = match.group(1).strip()

                if len(vendor) > 3:
                    return vendor

            # Next few lines
            for j in range(i + 1, min(i + 5, len(lines))):

                vendor = lines[j].strip()

                if (
                    vendor
                    and "PO NUMBER" not in vendor.upper()
                    and "PO DATE" not in vendor.upper()
                    and "GST" not in vendor.upper()
                    and len(vendor) > 3
                ):
                    return vendor

    return ""


def extract_description(text):

    text = re.sub(r"\s+", " ", text)

    patterns = [

        r"PURCHASE\s+ORDER\s+FOR\s+(.*?)\s+TO\s+GOLDFINCH",

        r"PURCHASE\s+ORDER\s+FOR\s+(.*?)\s+AT\s+GOLDFINCH",

        r"WORK\s+ORDER\s+FOR\s+(.*?)\s+TO\s+GOLDFINCH",

        r"WORK\s+ORDER\s+FOR\s+(.*?)\s+AT\s+GOLDFINCH",

        r"SUB:\s*(.*?)\s+TO\s+GOLDFINCH",

        r"SUB:\s*(.*?)\s+AT\s+GOLDFINCH"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            desc = match.group(1)

            desc = re.sub(
                r"PURCHASE\s+ORDER\s+FOR",
                "",
                desc,
                flags=re.IGNORECASE
            )

            desc = re.sub(
                r"WORK\s+ORDER\s+FOR",
                "",
                desc,
                flags=re.IGNORECASE
            )

            return clean_text(desc)

    return ""


def extract_po_data(uploaded_file):

    text = extract_text_from_pdf(uploaded_file)

    with st.expander(
        f"Extracted Text - {uploaded_file.name}"
    ):
        st.text(text[:15000])

    vendor = extract_vendor(text)

    description = extract_description(text)

    return {
        "Material Vendor": vendor,
        "Description (Scope of Work in Brief)": description,
        "File Name": uploaded_file.name
    }
