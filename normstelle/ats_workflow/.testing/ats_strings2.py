
antragsnummer = "172-2025"
tkz = "01044413"
bezeichnung = "Argon 4.6"

email_subject = f"ATS {antragsnummer} - TKZ {tkz} - {bezeichnung.upper()}"

root_path = r"\\deberdna-c010a\GlobalDE\DocumentManagement\NormstelleShare\TeileundStoffe"

ats_path = fr"{root_path}\Antrag\2025"
sdb_path = f"{root_path}\Sicherheitsdatenblatt"
pdb_path = f"{root_path}\Datenblatt"
info_path = f"{root_path}\Sonstiges"
coc_path = f"{root_path}\Zulassung"



ats_filename = f"{antragsnummer}_{tkz}"
sdb_filename = f"{antragsnummer}_{tkz}_SDB"
pdb_filename = f"{antragsnummer}_{tkz}_PDB"
coc_filename = f"{antragsnummer}_{tkz}_COC"
info_filename = f"{antragsnummer}_{tkz}_INFO"

print(f"\033[91m{ats_path}\{ats_filename}\033[0m")
print(f"\033[91m{sdb_path}\{sdb_filename}\033[0m")
print(f"\033[91m{pdb_path}\{pdb_filename}\033[0m")
print(f"\033[91m{info_path}\{info_filename}\033[0m")
print(f"\033[91m{coc_path}\{coc_filename}\033[0m")
print(f"\033[92m{email_subject}\033[0m")