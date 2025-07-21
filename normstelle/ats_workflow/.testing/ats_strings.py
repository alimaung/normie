
antragsnummer = "112-2025"
tkz = "01044339"
bezeichnung = "WD-40 MULTIFUNKTIONELL - (Aerosol)"

email_subject = f"ATS {antragsnummer} - TKZ {tkz} - {bezeichnung.upper()}"


sdb_filename = f"{antragsnummer}_{tkz}_SDB"
ats_filename = f"{antragsnummer}_{tkz}"
pdb_filename = f"{antragsnummer}_{tkz}_PDB"
coc_filename = f"{antragsnummer}_{tkz}_COC"
mlc_filename = f"{antragsnummer}_{tkz}_MLC"







print(f"\033[92m{email_subject}\033[0m")