
from openpyxl import Workbook
from openpyxl.styles import Font

def create_excel_report(df, exc_df, path):
    wb = Workbook()

    ws = wb.active
    ws.title = "PO Summary"

    headers = list(df.columns)

    for col_num, h in enumerate(headers, start=1):
        c = ws.cell(row=1, column=col_num)
        c.value = h
        c.font = Font(bold=True)

    for r, row in enumerate(df.values.tolist(), start=2):
        for c, val in enumerate(row, start=1):
            ws.cell(row=r, column=c, value=val)

    ws2 = wb.create_sheet("Exceptions")

    if not exc_df.empty:
        headers2 = list(exc_df.columns)
        for col_num, h in enumerate(headers2, start=1):
            ws2.cell(row=1, column=col_num, value=h)

        for r, row in enumerate(exc_df.values.tolist(), start=2):
            for c, val in enumerate(row, start=1):
                ws2.cell(row=r, column=c, value=val)

    wb.save(path)
