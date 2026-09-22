
import streamlit as st
import pandas as pd
from po_extractor import extract_po_data
from excel_exporter import create_excel_report

st.set_page_config(page_title="PO OCR Extractor", layout="wide")
st.title("PO OCR Extractor")

files = st.file_uploader(
    "Upload PO PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("Process PDFs") and files:
    records = []
    exceptions = []

    progress = st.progress(0)

    for i, f in enumerate(files):
        try:
            records.append(extract_po_data(f))
        except Exception as e:
            exceptions.append({
                "File Name": f.name,
                "Issue": str(e)
            })

        progress.progress((i + 1) / len(files))

    df = pd.DataFrame(records)
    exc_df = pd.DataFrame(exceptions)

    st.subheader("Results")
    st.dataframe(df, use_container_width=True)

    excel_bytes = create_excel_report(df, exc_df)

    st.download_button(
        "Download Excel",
        data=excel_bytes,
        file_name="PO_Summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
