
import streamlit as st
import pandas as pd
from modules.po_extractor import extract_po_data
from modules.excel_exporter import create_excel_report

st.set_page_config(page_title="PO Extractor", layout="wide")

st.title("Purchase Order Extractor")

files = st.file_uploader(
    "Upload Purchase Order PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("Process PDFs") and files:
    records = []
    exceptions = []

    for f in files:
        try:
            data = extract_po_data(f)
            data["File Name"] = f.name
            records.append(data)
        except Exception as e:
            exceptions.append({
                "File Name": f.name,
                "Issue": str(e)
            })

    df = pd.DataFrame(records)
    exc_df = pd.DataFrame(exceptions)

    st.dataframe(df)

    output_file = "/mnt/data/PO_Summary.xlsx"
    create_excel_report(df, exc_df, output_file)

    with open(output_file, "rb") as fp:
        st.download_button(
            "Download Excel",
            fp,
            file_name="PO_Summary.xlsx"
        )
