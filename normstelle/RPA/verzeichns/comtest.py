import win32com.client
from pathlib import Path
import time

excel_app = win32com.client.Dispatch("Excel.Application")
excel_app.Visible = True
excel_app.DisplayAlerts = False

verzeichnis_file_path=r"Q:\DocumentManagement\NormstelleShare\TeileundStoffe\Datei\Verzeichnis.xlsb"
path = Path(verzeichnis_file_path)
workbook = excel_app.Workbooks.Open(str(path))
print("workbook:", workbook)

worksheet = workbook.Worksheets(1)
print("workbook:", worksheet)

used_range = worksheet.UsedRange
last_row = used_range.Rows.Count

print(last_row)