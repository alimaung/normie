ATS Workflow

General

CMSR - Consumables and Materials Supply Request
ATS - Antrag für Teile und Stoffe
 

Application/Request Document goes through 6 stages:

1. Applicant
2. UUB (Hazards assessment)
3. UWS (Environment)
4. HSE (Health and Safety)
5. LAB (Manufacturing Lab)
6. NRM (Standardization Office)

Workflow for each stage:

1. Email (In) 

e.g. incoming CMSR from applicant or processed CMSR by UUB

1.1. ATS detector (Is a email likely ATS related or not?)
    - Attachments, subject, body, keywords
1.2. Stage detector (Which stage is this ATS)
    - Attachments (is there a valid CMSR form -> 2.), sender
1.3 Download/Extract attachments to staging area


2. PDF analysis

e.g. extracting relevant information



3. Excel analysis

e.g. looking up similar/existing products, 


4. Excel write

- Write collected information (like product name, applicant) to ATS sheet

5. PDF write

- Update PDF with new information e.g. new Application IDs, TKZ (PNs)

6. File operations

- Rename ATS, SDS, TDS with common string formats:

ATS: XXX/YYYY_XXXXXXXX.pdf
SDS: XXX/YYYY_XXXXXXXX_SDS.pdf
TDS: XXX/YYYY_XXXXXXXX_TDS.pdf

- Copy files to respectful live directories:

ATS: Antrag/YYYY/ 
SDS: Sicherheitsdatenblatt/
TDS: Datenblatt/

6. Email (Out)

- Compose email to recipient
- Attach emails if needed





Types of filetypes:

1. Application Form (T00221.pdf)
2. MSDS (.pdf)
3. TDS/PDS (.pdf)
4. COC 
5. TEST REPORTS