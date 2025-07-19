import pandas as pd

# Load JSON into DataFrame
json = "json.json"
df = pd.read_json(json)

# Optional: preview the DataFrame
print(df)

# Color palette (ANSI codes)
colors = [
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
    "\033[97m",  # White
]

reset = "\033[0m"

rows = []

for i, r in df.iterrows():
    ats_raw = r[0]
    ats = ats_raw.replace("/", "-")
    tkz = r[1]
    bez = r[5]
    rows.append([ats, tkz, bez])

    email_subject = f"ATS {ats} - TKZ {tkz} - {bez.upper()}"
    sdb_filename = f"{ats}_{tkz}_SDB"
    ats_filename = f"{ats}_{tkz}"
    pdb_filename = f"{ats}_{tkz}_PDB"
    coc_filename = f"{ats}_{tkz}_COC"
    mlc_filename = f"{ats}_{tkz}_MLC"

    color = colors[i % len(colors)]

    print(f"{color}{email_subject}")
    print(ats_filename)
    print(sdb_filename)
    print(pdb_filename + reset)
    print(f"{ats}\t{tkz}\t\t{bez}")
    print("\n")
    print(coc_filename)
    print(mlc_filename + reset)