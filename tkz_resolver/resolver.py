import pandas as pd



df = pd.read_excel(r"Y:\normie\tkz_resolver\Kopie von RR Anlagen und Kommentare.xlsx")

for row in df.iterrows():
    #print(row[1]['interne Bezeichnung'])
    break

df2 = pd.read_excel(r"Y:\normie\tkz_resolver\TKZ_AT&S_export_2024_04_24.xlsx")

for row in df2.iterrows():
    print(row[1]['Internal Name'])
    # Get background color of the row
    workbook = pd.ExcelFile(r"Y:\normie\tkz_resolver\TKZ_AT&S_export_2024_04_24.xlsx")
    sheet = workbook.book.active
    row_number = row[0] + 2  # Add 2 because Excel rows are 1-based and header row
    cell = sheet.cell(row=row_number, column=1)
    bg_color = cell.fill.start_color.index
    print(f"Background color: {bg_color}")
    break




