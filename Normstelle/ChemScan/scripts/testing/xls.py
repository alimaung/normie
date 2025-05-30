import pandas as pd
import time
import openpyxl

FILEPATH = r"P:\k-z\Ofs\Normstelle\Teile-und-Stoffe\Chemscan\Ali.xlsx"

df = pd.read_excel(FILEPATH)

#print(df)

for index, row in df[::-1].iterrows():
    print(index)
    break

wb = openpyxl.load_workbook(FILEPATH)
ws = wb.active
row_index = df.index[-1] + 2

colors = []

for cell in ws[row_index]:
    fill = cell.fill.start_color.rgb
    if fill is not None and fill !="000000000":
        hex_color = f"#{fill[2:]}"
    else:
        hex_color = None
    colors.append(hex_color)

print(colors)