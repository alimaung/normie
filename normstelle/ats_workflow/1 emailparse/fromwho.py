# detect which emails are ongoing ATS applications, usually by sender and attachments/subject

# Departments: (locations are OU and DW, they have different departments)

# IRM-Standartization-Office@rolls-royce.com -> Standardization Office (us, for both OU and DW)
# i.eiser@uub-schwan, n.dibbert@uub-schwan -> ChemScan (UUB, for both OU and DW)
# karsten.bartz@rolls-royce.com -> Umweltschutz (UWS, for both OU and DW)
# hse-newsou@rolls-royce.com -> Arbeit- und Gesundheitsschutz (HSE OU) | hs-e-teamdw@rolls-royce.com -> Arbeit- und Gesundheitsschutz (HSE DW)
# ralph.gros@rolls-royce.com -> Fertigungslabor (LAB OU) | rrd-materials-spg@rolls-royce.com -> Fertigungslabor (LAB DW)

# If sender is any of these, its high probability that its an ongoing ATS application
# 
# For ChemScan:
# If subject contains: "ChemScan: Stellungnahmen ...""
# If body contains: "anbei erhalten Sie folgende Stellungnahmen:", 
# If a attachment contains pdf with "Stellungnahme_...."
# If attachment is a valid ATS form (detected by ats_parser)

# For UWS:
# If body contains: "der Teil Umweltschutz der Anträge ist bearbeitet. Anbei die signierten Formulare."
# If attachment contains suffix: "... (002)" (with whitespace: " (002)")
# If attachment is a valid ATS form (detected by ats_parser)

# For HSE OU:

# If body contains: "anbei die Freigabe", "Anouar"
# If attachment is valid ATS form (detected by ats_parser)

# For HSE DW:

# TODO: HSEDW has special handling, where it doesnt contain any attachments, but there is a link in the previous email (usually its included) 
# which we need to extract: this is the root link \\deberdna-c011a\Projekte\HS&E RRD\public\TEILE_STOFFE_BEARBEITUNG TEMPORÄR\<attachments>

# If body contains: "der Antrag ist bearbeitet und freigegeben", "bearbeitet und freigegeben", "die Anträge sind bearbeitet und freigegeben"
# If sender is "uta.samuels@rolls-royce.com",
# optional: if CC is "hs-e-teamdw@rolls-royce.com"
# rarely: if attachment: if it is a valid ATS form (detected by ats_parser)

# For LAB OU:






