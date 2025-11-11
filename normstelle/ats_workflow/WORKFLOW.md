# ATS Workflow Architecture

## Overview

This document describes the 3-stage email processing workflow for ATS (Antrag für Teile und Stoffe) applications. The workflow is designed to automatically classify and route emails through the appropriate processing pipelines.

### Global Workflow Context

**Shared Inbox Architecture**: All emails from all workflow stages arrive in a **shared inbox**. The system continuously monitors this inbox and processes emails based on their type and stage:

- **NEW ATS**: Initial application from applicant
- **ONGOING ATS**: Emails returning from departments (UUB, UWS, HSE, LAB, Final)
- **CHANGE ATS**: Change requests for existing approved materials

**Continuous Loop**: Each stage sends an email back to the shared inbox, which triggers the next processing step. This creates a continuous cycle where:
1. Email arrives → Process → Send to next stage
2. Email returns from department → Process → Send to next stage
3. Repeat until final approval

**File System**: All files (`.msg`, ATS forms, SDS, TDS, COC) are stored on a **shared network drive**. Excel hyperlinks (columns M-Q in Verzeichnis) point to these files for easy access.

## Definitions

- **ATS**: Antrag für Teile und Stoffe (Application for Parts and Materials)
- **CMSR**: Consumables and Materials Supply Request
- **TKZ**: Teilkennzahl (Part Number)
- **HITL**: Human-In-The-Loop (manual review workflow)

## Workflow Stages

The ATS approval process goes through 6 stages:

1. **Applicant** - Initial application submission
2. **UUB (ChemScan)** - Hazards assessment by Umwelt- und Unternehmensberatung Schwan
3. **UWS** - Environment protection evaluation
4. **HSE** - Health, Safety & Environment evaluation
5. **LAB** - Manufacturing Laboratory evaluation
6. **NRM** - Standardization Office final approval

## 3-Stage Email Processing Workflow

### Stage 1: ATS Detector

**Purpose**: Fast, lightweight filter to identify ATS-related emails

**Processing**:
- Subject line keyword matching: "Antrag", "ATS", "AfTS", "Teile und Stoffe", etc.
- Attachment filename pattern matching: `.*ats.*`, `.*sds.*`, `.*tds.*`, etc.
- Sender filtering: Ignore internal standardization office emails

**Output**: `ATS_PROBABILITY` (HIGH | MEDIUM | LOW | NONE)

**Routing**:
- If `NONE` → Stop processing, archive email
- If `HIGH` or `MEDIUM` → Proceed to Stage 2

**Implementation**: See `1 emailparse/score_msg.py` and `1 emailparse/mailscorer.py`

---

### Stage 2: Stage Detector

**Purpose**: Classify email type and determine workflow stage

#### 2a. Type Classification

Classify the email as one of three types:

**NEW ATS** (Completely new materials):
- **Field 1 (Request No.)**: Empty or not assigned (no XXX/YYYY format)
- **Field 51 (TKZ)**: Empty or not assigned
- **Form completion**: Only Fields 2-21 filled (applicant section)
- **Fields 22-50**: Empty (no department signatures)
- **Sender**: Applicant domain (not department email)
- **Subject**: Basic keywords, no ATS number pattern

**ONGOING** (New materials in process):
- **Field 1**: Has ATS number (XXX/YYYY format) - already assigned
- **Field 51**: May or may not have TKZ yet
- **Form completion**: Fields 22+ have some signatures (workflow in progress)
- **Sender**: Department email OR Standardisation Office forwarding
- **Subject**: Contains ATS number and/or TKZ

**CHANGE** (Change of existing approved material):
- **Field 1**: Has ATS number
- **Field 5**: "Change in Demand" checked
- **Field 20**: References previous ATS number
- **Field 51**: Has TKZ (already assigned)
- **Status**: Currently inactive branch - flag/tag for future handling

**Output**: `TYPE` (NEW | ONGOING | CHANGE | UNKNOWN)

#### 2b. Ongoing Stage Detection

**Only executed if `TYPE = ONGOING`**

Detect which workflow stage the application is currently at:

**ONGOING_STAGE_2** (ChemScan/UUB):
- Fields 2-24 filled (applicant + ChemScan section)
- Fields 25-50 empty
- Sender: `gefahrstoffmanagement@uub-schwan.de`
- Subject: May contain "ChemScan: Stellungnahmen"
- Attachments: ChemScan report PDF

**ONGOING_STAGE_3** (UWS):
- Fields 2-31 filled (applicant + ChemScan + UWS)
- Fields 32-50 empty
- Sender: `karsten.bartz@rolls-royce.com`
- Body: "der Teil Umweltschutz der Anträge ist bearbeitet"
- Attachments: May have " (002)" suffix

**ONGOING_STAGE_4** (HSE):
- Fields 2-38 filled (applicant + ChemScan + UWS + HSE)
- Fields 39-50 empty
- Sender: `hse-newsou@rolls-royce.com` (OU) or `hs-e-teamdw@rolls-royce.com` (DW)
- Body: "anbei die Freigabe" (OU) or "der Antrag ist bearbeitet und freigegeben" (DW)

**ONGOING_STAGE_5** (LAB):
- Fields 2-49 filled (applicant + ChemScan + UWS + HSE + LAB)
- Field 50 empty
- Sender: `ralph.gross@rolls-royce.com` (OU) or `rrd-materials-spg@rolls-royce.com` (DW)

**ONGOING_STAGE_6** (Final Approval):
- Fields 2-50 filled (all sections complete)
- Sender: `CBS-Standardisation-Office@Rolls-Royce.com`

**Output**: `STAGE` (2 | 3 | 4 | 5 | 6 | UNKNOWN)

**Implementation**: See `1 emailparse/fromwho.py` (planning notes)

---

### Stage 3: Workflow Router

**Purpose**: Route to appropriate processing pipeline based on classification

**Routing Logic**:

| TYPE | Action |
|------|--------|
| `NEW` | → `new_workflow` pipeline |
| `ONGOING` | → `ongoing_workflow` with `STAGE` parameter |
| `CHANGE` | → Flag/tag, ignore processing (future handling) |
| `UNKNOWN` | → Manual review queue (HITL) |

#### NEW Workflow Pipeline

**Purpose**: Process completely new ATS applications

**Detailed Steps**:

1. **Extract Attachments to Staging Area**
   - Extract all PDF attachments from `.msg` file
   - Save to temporary staging directory

2. **Attachment Classification**
   - Run ATS form detector (`2 pdfparser/ats/`) → Identify T00221 form
   - Run SDS detector (`2 pdfparser/sds/sds_detector.py`) → Identify Safety Data Sheets
   - Run TDS detector (`2 pdfparser/tds/tds_detector.py`) → Identify Technical Data Sheets
   - Run COC detector (if available) → Identify Certificates of Conformity
   - Classify each attachment: `{ats_form: [path], sds: [paths], tds: [paths], coc: [paths], unknown: [paths]}`

3. **PDF Analysis: Extract ATS Form Data**
   - Extract all form fields (2-21) from ATS form PDF
   - Validate Field 5 = "Neubedarf" (new requirement)
   - Extract product information, applicant details, etc.

4. **SDS Validation**
   - Check if SDS detected and Field 18a = "Ja" (SDS required)
   - Validate SDS language: Must be German (detected by SDS detector)
   - Validate SDS date: Must be <2 years old (`sds_date_detector.py`)
   - Extract CAS numbers for MLC132 check (`cas_extractor.py`)
   - If invalid → Flag for applicant notification

5. **TDS Validation**
   - Check if TDS detected and Field 18b = "Ja" (TDS required)
   - Validate TDS completeness (optional)

6. **Completeness Check**
   - Verify all required fields filled (Fields 2-21)
   - Verify required attachments present (SDS, TDS if indicated)
   - Generate list of missing information

7. **MLC132 Check** (Prohibited Substances)
   - Extract CAS numbers from SDS Section 3
   - Check against MLC132 prohibited substances list
   - If hit found → Route directly to Environmental Protection and HSE

8. **Excel Lookup**
   - Check for duplicates in `Verzeichnis.xlsb`
   - Search for similar products in `Teilenummern 0104....xls`

9. **ID Generation**
   - Generate ATS number (XXX/YYYY) from `Verzeichnis.xlsb` (increment last number for current year)
   - Generate TKZ (0104XXXX) from `Teilenummern 0104....xls` (increment last number)
   - Reserve IDs (don't use until successful processing)

10. **Generate Response Email** (if missing information)
    - Create email template listing missing fields/attachments
    - Request valid SDS (German, <2 years) if invalid
    - Request missing attachments if indicated but not provided

11. **Excel Write**
    - Create new row in `Verzeichnis.xlsb` with extracted data
    - Create new row in `Teilenummern 0104....xls` (TKZ sheet)
    - Write hyperlinks to files (columns M-Q) - will be filled after file operations

12. **PDF Write**
    - Fill Field 1 (Request No.) with generated Antragsnummer (XXX/YYYY)
    - Fill Field 51 (TKZ) with generated part number (0104XXXX)
    - Preserve all existing form data and structure

13. **File Operations**
    - Rename ATS form: `XXX-YYYY_XXXXXXXX_ATS.pdf` (e.g., `157-2025_01044395_ATS.pdf`)
    - Rename SDS: `XXX-YYYY_XXXXXXXX_SDB.pdf` (if detected)
    - Rename TDS: `XXX-YYYY_XXXXXXXX_TDB.pdf` (if detected)
    - Rename COC: `XXX-YYYY_XXXXXXXX_COC.pdf` (if detected)
    - Save to shared network drive:
      - ATS: `\\network\drive\Antrag\YYYY\XXX-YYYY_XXXXXXXX_ATS.pdf`
      - SDS: `\\network\drive\Sicherheitsdatenblatt\XXX-YYYY_XXXXXXXX_SDB.pdf`
      - TDS: `\\network\drive\Datenblatt\XXX-YYYY_XXXXXXXX_TDB.pdf`
    - Create file paths for Excel hyperlinks

14. **Excel Hyperlink Update**
    - Update column M: Hyperlink to ATS PDF
    - Update column P: Hyperlink to SDS (if Field 18a = "Ja" and SDS detected)
    - Update column N: Hyperlink to TDS (if Field 18b = "Ja" and TDS detected)
    - Update column O: Hyperlink to COC (if detected)
    - Update column Q: Hyperlink to Gefährdungsbeurteilung (if Field 18c = "Ja")

15. **Email (Out)**
    - If missing information: Send request email to applicant
    - If complete: Send confirmation to applicant with ATS number and TKZ
    - Forward to UUB for ChemScan evaluation (if SDS present and MLC132 check passed)

**Implementation**: 
- `normstelle/RPA/verzeichns/` - Main workflow scripts
- `2 pdfparser/ats/` - ATS form parsing
- `2 pdfparser/sds/` - SDS detection and validation
- `2 pdfparser/tds/` - TDS detection
- `3 mlc check/` - MLC132 prohibited substances check
- `5 excel/` - Excel read/write operations
- `6 files/` - File operations and renaming

#### ONGOING Workflow Pipeline

**Purpose**: Process ATS applications that are in the approval workflow

**Detailed Steps**:

1. **Extract Attachments to Staging Area**
   - Extract all PDF attachments from `.msg` file
   - May include: Updated ATS form, ChemScan report, other documents

2. **Attachment Classification**
   - Run ATS form detector → Identify updated T00221 form
   - Run ChemScan detector (`2 pdfparser/chemscan/`) → Identify ChemScan reports (Stage 2)
   - Run SDS/TDS detectors → Identify any new/updated data sheets
   - Classify attachments by type

3. **Read Existing IDs from PDF**
   - Extract Field 1 (Request No.) → Get ATS number (XXX/YYYY)
   - Extract Field 51 (TKZ) → Get part number (0104XXXX)
   - Do NOT generate new IDs (already assigned)

4. **PDF Analysis: Extract Updated Data**
   - Extract updated form fields based on current stage:
     - **Stage 2**: Fields 22-24 (ChemScan section)
     - **Stage 3**: Fields 25-31 (UWS section)
     - **Stage 4**: Fields 32-38 (HSE section)
     - **Stage 5**: Fields 39-49 (LAB section)
     - **Stage 6**: Field 50 (Final approval)
   - Extract new signatures and evaluations
   - Extract ChemScan report data (if Stage 2)

5. **Excel Lookup**
   - Find existing entry in `Verzeichnis.xlsb` by ATS number
   - Verify TKZ matches
   - Read current status

6. **Excel Write: Update Existing Row**
   - Update status field (Column C)
   - Update department signature fields
   - Update stage-specific columns
   - Preserve existing data

7. **PDF Write: Update Form**
   - Update form with new signatures/evaluations
   - Preserve all existing data
   - Maintain form structure

8. **File Operations**
   - Update/replace ATS form on network drive (if form updated)
   - Save new ChemScan report (Stage 2): `XXX-YYYY_XXXXXXXX_ChemScan.pdf`
   - Update file paths if files changed
   - Maintain existing file organization

9. **Excel Hyperlink Update** (if files changed)
   - Update hyperlinks in columns M-Q if new files added/replaced

10. **Email (Out): Forward to Next Stage**
    - **Stage 2 → Stage 3**: Forward to UWS (`karsten.bartz@rolls-royce.com`)
    - **Stage 3 → Stage 4**: Forward to HSE (OU or DW based on location)
    - **Stage 4 → Stage 5**: Forward to LAB (OU or DW based on location)
    - **Stage 5 → Stage 6**: Forward to Standardisation Office for final approval
    - **Stage 6 → Complete**: Send approval notification email (broadcast to all relevant departments)

**Stage-Specific Details**:

- **Stage 2 (ChemScan/UUB)**:
  - Extract ChemScan report from attachments
  - Update Fields 22-24 with ChemScan evaluation results
  - Save ChemScan report to network drive
  - Forward to UWS (Environmental Protection)

- **Stage 3 (UWS)**:
  - Extract UWS evaluation from Fields 25-31
  - Check for approval/rejection in Field 26
  - Forward to HSE (OU or DW based on Field 12 - Einsatzort)

- **Stage 4 (HSE)**:
  - Extract HSE evaluation from Fields 32-38
  - Check for approval/rejection in Field 33
  - Check Field 34 (HS&E-relevant?) for hazardous substances register entry
  - Forward to LAB (OU or DW)

- **Stage 5 (LAB)**:
  - Extract LAB evaluation from Fields 39-49
  - Check Field 39 (Product approval status)
  - May be "release for first order" (Fields 40-46) or "release for use" (Fields 47-49)
  - Forward to Standardisation Office

- **Stage 6 (Final Approval)**:
  - Extract final approval from Field 50
  - Update Excel: Mark as approved/rejected
  - Update SAP (if required)
  - Upload to ChemScan database (if HS&E-relevant)
  - Send broadcast email to all relevant departments and applicant

**Implementation**: 
- `normstelle/RPA/verzeichns/` - Excel update scripts (needs modification for ONGOING)
- `2 pdfparser/ats/` - ATS form parsing (extract updated fields)
- `2 pdfparser/chemscan/` - ChemScan report detection and parsing
- `5 excel/` - Excel update operations
- `6 files/` - File update operations

#### CHANGE Workflow Pipeline

**Status**: Currently inactive (flag/tag for future handling)

**Characteristics**:
- Field 1: Has ATS number (already assigned)
- Field 5: "Bedarfsänderung" (Change in Demand) checked
- Field 20: References previous ATS number
- Field 51: Has TKZ (already assigned)

**Future Handling** (when implemented):
- Read existing IDs from PDF (Field 1, Field 51)
- Identify change type (manufacturer, location, packaging, etc.)
- Update specific Excel fields based on change type
- Preserve historical data
- Same file operations as ONGOING (update existing files)
- Special routing based on change type

**Currently**: Flag/tag for manual review queue

---

## HITL (Human-In-The-Loop) Integration

**Confidence Scoring**:
- Each classification includes a confidence score (0.0 - 1.0)
- Low confidence (< 0.7): Flag for human review but still process
- Very low confidence (< 0.5): Manual review queue only
- Human can override classification in frontend

**Future Enhancement**:
- Frontend interface for reviewing and labeling emails
- Background scanning with human review capability
- Training data collection for ML model improvement

---

## Email Processing Flow Diagram

```
Shared Inbox (all stages)
    ↓
Email Received (.msg file)
    ↓
[Stage 1: ATS Detector]
    - Subject keywords
    - Attachment filename patterns
    - Sender filtering
    ↓
ATS_PROBABILITY?
    ├─ NONE → Archive & Stop
    └─ HIGH/MEDIUM → Continue
    ↓
[Stage 2: Stage Detector]
    ↓
[2a: Type Classification]
    - Extract ATS form from attachments
    - Analyze Field 1, Field 5, Field 20, Field 51
    - Check sender domain
    ↓
TYPE?
    ├─ NEW → [2b: Skip] → [Stage 3: new_workflow]
    ├─ ONGOING → [2b: Stage Detection] → [Stage 3: ongoing_workflow(STAGE)]
    ├─ CHANGE → [2b: Skip] → Flag/Tag (Future)
    └─ UNKNOWN → Manual Review Queue
    ↓
[Stage 3: Workflow Router]
    ↓
Process according to TYPE and STAGE
    ↓
Email sent to next stage
    ↓
[Wait... email returns to shared inbox]
    ↓
[Repeat cycle]
```

## Detailed Workflow Steps

### Attachment Classification Step

**Purpose**: Identify and classify all PDF attachments from email

**Process**:
1. Extract all attachments from `.msg` file to staging area
2. For each PDF attachment, run detectors:
   - **ATS Form Detector** (`2 pdfparser/ats/`) → Is it T00221 form?
   - **SDS Detector** (`2 pdfparser/sds/sds_detector.py`) → Is it Safety Data Sheet?
   - **TDS Detector** (`2 pdfparser/tds/tds_detector.py`) → Is it Technical Data Sheet?
   - **ChemScan Detector** (`2 pdfparser/chemscan/`) → Is it ChemScan report? (ONGOING Stage 2)
   - **COC Detector** (if available) → Is it Certificate of Conformity?

**Output**: Classification dictionary
```python
{
    'ats_form': [path_to_ats.pdf],
    'sds': [path_to_sds.pdf],  # with validation results
    'tds': [path_to_tds.pdf],
    'chemscan': [path_to_chemscan.pdf],  # ONGOING only
    'coc': [path_to_coc.pdf],
    'unknown': [path_to_unknown.pdf]
}
```

**Validation**:
- **SDS**: Must be German, must be <2 years old (from instructions.md)
- **TDS**: Validate completeness (optional)
- If validation fails → Flag for applicant notification

**Usage**:
- File naming: Add appropriate suffix (_SDB, _TDB, _ChemScan, etc.)
- File organization: Save to correct directories
- Excel hyperlinks: Create links in columns M-Q
- Completeness check: Verify required attachments present

### File Operations Step

**Purpose**: Rename, organize, and save files to shared network drive

**Position in Workflow**: After PDF write (IDs filled), before Excel hyperlink update

**Process**:

1. **File Naming** (using generated/read IDs):
   - ATS form: `XXX-YYYY_XXXXXXXX_ATS.pdf` (e.g., `157-2025_01044395_ATS.pdf`)
   - SDS: `XXX-YYYY_XXXXXXXX_SDB.pdf`
   - TDS: `XXX-YYYY_XXXXXXXX_TDB.pdf`
   - COC: `XXX-YYYY_XXXXXXXX_COC.pdf`
   - ChemScan: `XXX-YYYY_XXXXXXXX_ChemScan.pdf` (ONGOING Stage 2)
   - Test reports: `XXX-YYYY_XXXXXXXX_TEST.pdf`
   - Other: `XXX-YYYY_XXXXXXXX_INFO.pdf`

2. **Directory Structure** (Shared Network Drive):
   - ATS forms: `\\network\drive\Antrag\YYYY\` (organized by year)
   - SDS: `\\network\drive\Sicherheitsdatenblatt\`
   - TDS: `\\network\drive\Datenblatt\`
   - COC: (to be determined)
   - ChemScan: (to be determined)

3. **File Operations**:
   - **NEW**: Create new files with IDs in filename
   - **ONGOING**: Update/replace existing files (maintain same filename)
   - Copy files to appropriate network drive directories
   - Preserve file structure and organization

4. **Return File Paths**:
   - Return absolute paths for Excel hyperlink creation
   - Format: `\\network\drive\Antrag\2025\157-2025_01044395_ATS.pdf`

**Excel Hyperlink Mapping**:
- Column M: Hyperlink to ATS PDF
- Column N: Hyperlink to TDS (if Field 18b = "Ja" and TDS detected)
- Column O: Hyperlink to COC (if detected)
- Column P: Hyperlink to SDS (if Field 18a = "Ja" and SDS detected)
- Column Q: Hyperlink to Gefährdungsbeurteilung (if Field 18c = "Ja")

**Implementation**: See `6 files/renamer.py` (planning notes)

---

## Key Form Fields Reference (T00221)

**Applicant Section** (Fields 2-21):
- Field 1: Request No. (XXX/YYYY) - Assigned by Standardisation Office
- Field 5: Identification of Request (New Demand / Change in Demand)
- Field 20: Reference to past requests
- Field 51: Part Number (TKZ) - Assigned by Standardisation Office

**Department Sections**:
- Fields 22-24: ChemScan (UUB)
- Fields 25-31: Environmental Protection Officer (UWS)
- Fields 32-38: Occupational Health & Safety (HSE)
- Fields 39-49: Manufacturing Laboratory (LAB)
- Field 50: Standardisation Office (Final approval)

---

## Department Email Addresses

| Department | Email Address | Location |
|------------|---------------|----------|
| ChemScan (UUB) | gefahrstoffmanagement@uub-schwan.de | Both OU/DW |
| Environmental Protection (UWS) | karsten.bartz@rolls-royce.com | Both OU/DW |
| HSE OU | hse-newsou@rolls-royce.com | OU |
| HSE DW | hs-e-teamdw@rolls-royce.com | DW |
| LAB OU | ralph.gross@rolls-royce.com | OU |
| LAB DW | rrd-materials-spg@rolls-royce.com | DW |
| Standardisation Office | CBS-Standardisation-Office@Rolls-Royce.com | Both OU/DW |

---

## Module Integration Points

### Email Processing (`1 emailparse/`)
- `score_msg.py` - Single .msg file ATS probability scoring
- `mailscorer.py` - Batch email scoring
- `msgparser.py` - Extract attachments and split email threads
- **Integration**: Extract attachments, score emails, pass to Stage 2

### PDF Parsing (`2 pdfparser/`)
- `ats/` - ATS form (T00221) parsing and field extraction
- `sds/` - SDS detection, date validation, CAS extraction
- `tds/` - TDS/PDS detection
- `chemscan/` - ChemScan report detection and parsing (ONGOING Stage 2)
- `coc/` - Certificate of Conformity detection (if available)
- **Integration**: Classify attachments, extract data, validate requirements

### MLC Check (`3 mlc check/`)
- Prohibited substances checking using CAS numbers
- **Integration**: After SDS CAS extraction, before workflow routing

### Excel Operations (`5 excel/` and `normstelle/RPA/verzeichns/`)
- `verzeichns/` - ID generation, Excel writing for NEW applications
- **Integration**: Generate/read IDs, create/update Excel rows, write hyperlinks

### File Operations (`6 files/`)
- File renaming with ID format
- Network drive organization
- **Integration**: After PDF write, before Excel hyperlink update

## Key Requirements

### SDS Validation Requirements (from instructions.md)
- Must be **German language** (detected by SDS detector)
- Must be **<2 years old** (validated by SDS date detector)
- Must be **EU-compliant** (structure validation)
- If invalid → Generate email to applicant requesting valid SDS

### File Naming Convention
- Format: `XXX-YYYY_XXXXXXXX_TYPE.pdf`
- Example: `157-2025_01044395_SDB.pdf`
- Types: `_ATS`, `_SDB`, `_TDB`, `_COC`, `_ChemScan`, `_TEST`, `_INFO`

### Network Drive Structure
- Files stored on shared network drive accessible by all departments
- Excel hyperlinks (columns M-Q) point to these files
- Organized by document type and year (for ATS forms)

## Related Documentation

- `README.md` - General workflow overview
- `1 emailparse/README.md` - Email parsing scripts documentation
- `normstelle/RPA/verzeichns/README.md` - Verzeichnis automation scripts
- `.docs/Forms/AAW11-03_Bearbeitung der Anträge für Teile und Stoffe-Version1.0.md` - Process description
- `.docs/Forms/01030063-AA.md` - Form completion instructions
- `.docs/instructions.md` - T00221 form field descriptions

