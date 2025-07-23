import pandas as pd
import json

# Read the Excel file with date parsing to avoid overflow errors
xls = pd.read_excel(r"MLC_list.xlsx", parse_dates=True)

# Extract the relevant columns (A2 - H10543)
df = xls.iloc[1:10543, 0:8]  # Adjusting for zero-based indexing

# Save to CSV
df.to_csv(r"mlc_list.csv", index=False)

# Save to json
df.to_json(r"mlc_list.json", orient="records", date_format='iso')

# Save unique values of columns E-H to a json file, with the column name as the key and its unique values as the value
unique_values = {
    "E": df.iloc[:, 4].unique().tolist(),
    "F": df.iloc[:, 5].unique().tolist(),
    "G": df.iloc[:, 6].unique().tolist(),
    "H": df.iloc[:, 7].unique().tolist()
}

# Save unique values to json
with open(r"unique_values.json", "w") as json_file:
    json.dump(unique_values, json_file)







