# detect which emails are ongoing/incoming ATS applications, usually by subject, sender and/or attachments

# ATS applications are going through these stages:
# 1. Incoming application from applicant (incoming)
# 2. ChemScan evaluation by UUB
# 3. UWS evaluation by Karsten Bartz
# 4. HSE OU/DW evaluation by HSE OU/DW team
# 5. LAB OU/DW evaluation by LAB OU/DW team
# 6. Final approval through standardization office

# The ATS form undergoes changes during the process. The applicant fills in the form, and then the form is sent to standardization office for processing.
# After checking, we send the form+sds+tds to UUB for evaluation, they return the form with evaluation and signature plus a ChemScan report.
# After checking, we send the form+sds+tds+chemscan to UWS for evaluation, they return the form with evaluation and signature.
# After checking, we send the form+sds+tds+chemscan to HSE OU/DW team for evaluation, they return the form with evaluation and signature.
# After checking, we send the form+coc to LAB OU/DW team for evaluation, they return the form with evaluation and signature.
# Finally the standardization office can formally approve the application if all evaluations are approved. This is broadcasted to all relevant departments.

# The purpose of this script is to detect which emails are ongoing ATS applications, and at which stage they are or if they are new, untracked incoming applications.




# If subject contains a ATS number (XXX-YYYY format) and a TKZ (XXXXXXXX) in subject, its likely a ongoing ATS application
# If subject contains basic strings like "Antrag", "Antrag Teile und Stoffe", "AfTS" etc. its likely a incoming ATS application


# Departments: (locations are OU and DW, they have different departments)

# IRM-Standartization-Office@rolls-royce.com -> Standardization Office (us, for both OU and DW)
# i.eiser@uub-schwan, n.dibbert@uub-schwan -> ChemScan (UUB, for both OU and DW)
# karsten.bartz@rolls-royce.com -> Umweltschutz (UWS, for both OU and DW)
# hse-newsou@rolls-royce.com -> Arbeit- und Gesundheitsschutz (HSE OU) | hs-e-teamdw@rolls-royce.com -> Arbeit- und Gesundheitsschutz (HSE DW)
# ralph.gros@rolls-royce.com -> Fertigungslabor (LAB OU) | rrd-materials-spg@rolls-royce.com -> Fertigungslabor (LAB DW)

# If sender is any of above, its high probability that its an ongoing ATS application (these emails are used by ongoing ATS applications)
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






