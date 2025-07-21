# AAW 11-03 Processing of Requests for Parts and Materials

## Contents

1. **Objective and Purpose**
2. **Scope of Application**
3. **Responsibilities**
4. **Definitions and Terms**
5. **Description of Procedures**
   - 5.1 **Value Stream Diagram**
   - 5.2 **Process Flow Diagram**
   - 5.3 **General**
     - 5.3.1 **Aviation Legal Information on Request for Parts and Materials**
     - 5.3.2 **Occupational Safety Information**
     - 5.3.3 **Background on Part Numbers in SAP**
     - 5.3.4 **Background on Standard Parts and Semi-finished Products**
   - 5.4 **Processing of Requests for Parts and Materials**
     - 5.4.1 **Process Description**
     - 5.4.2 **Special Features**
     - 5.4.3 **Entry into Hazardous Substances Register**
   - 5.5 **Attachments**
6. **Applicable Documents**
7. **Change Record**
8. **Approval**

## 1. Objective and Purpose

The objective of this AAW is the processing of requests for parts and materials. The purpose of this AAW is to enable trained personnel to process requests for parts and materials. The essential steps are to be described so that trained personnel can work according to them.

## 2. Scope of Application

The AAW is valid for all employed as well as temporarily active employees of Iron Mountain (Deutschland) Service GmbH at the Rolls-Royce Deutschland locations.

## 3. Responsibilities

The team leader of the Standardisation Office is responsible for the creation and maintenance of this AAW. Trained personnel is responsible for compliance with the requirements from this AAW.

| Responsibility | Assignment to Section BFH | Assignment to GP/WI/N |
|----------------|---------------------------|----------------------|
| Standardisation Office (OU) | AAW11 | RRTI00032 |

## 4. Definitions and Terms

| Abbreviation | Description |
|--------------|-------------|
| exDiMS | Document Information Management System |
| DW | Dahlewitz location |
| IRM | Iron Mountain (Deutschland) Service GmbH |
| MLC104 | Manufacturing Laboratories Catalogue (extracted from RR Global Consumables Catalogue with RR approved consumable, non metallic and proprietary products for use in new manufacture and overhaul and Repair) |
| MLC132 | Manufacturing Laboratories Catalogue (Elimination of Materials and chemical Substances from Products and Processes Policy) |
| N | Works Standard |
| OMat | Overhaul Materials (List of approved auxiliary and operating materials for Repair and Overhaul) |
| OU | Oberursel location |
| PDM | Product Data Management |
| REACh | Registration, Evaluation, Authorisation and Restriction of Chemicals |
| RR | Rolls-Royce plc |
| RRD | Rolls-Royce Deutschland Ltd & Co KG |
| RRT | Rolls-Royce Part Number |
| RRTI | Rolls-Royce Task Instruction |
| SAP | SAP (Systems, Applications and Product) is the resource planning program at Rolls-Royce |
| SDB | Safety Data Sheet |
| TKZ | Part Identifier (Part Number) |
| UUB-Schwan | Umwelt- und Unternehmensberatung Schwan GmbH |
| WI | Work Instruction |

## 5. Description of Procedures

### 5.1 Value Stream Diagram

**Input Event:** RRD Employees (all)

**IRM Processing:**
- Request receipt at IRM
- Release control by IRM

**Value Creation Results for RRD by IRM:**
- Product uniquely assigned to TKZ
- HS&E requirements evaluated by HS&E
- Procurement release
- Application release
- Product created in SAP (if required)
- HS&E-relevant products entered in hazardous substances register
- Technical evaluation by laboratory available
- Certificate requirement transferred to purchase order and goods receipt inspection (if required)
- ChemScan evaluation available
- Request and request documentation filed in traceable manner
- Request and ChemScan evaluation available in ChemScan database
- Environmental protection evaluation available

### 5.2 Process Flow Diagram

**Start:** Input "Request for Parts and Materials"

**01** → **Input Processing**

**Decision:** Information complete?
- **No** → Clarification with applicant required → **02** → Part number assignment
- **Yes** ↓

**Decision:** Product already numbered?
- **No** → Part number assignment → **02**
- **Yes** ↓ **03**

**03** → **Name request and complete**

**04** → **Check MLC132, request ChemScan & compile predecessor documents**

**05** → **Control of approval process**

**Decision:** Environmental protection approved?
- **No** → (Return to control)
- **Yes** ↓

**Decision:** HS&E approved?
- **No** → (Return to control)
- **Yes** ↓

**Decision:** Manufacturing laboratory approved?
- **No** → (Return to control)
- **Yes** ↓

**Two parallel paths:**

**Left Path:**
- **Release for first order for product approval**
- **Decision:** Release by standardisation office?
  - **Yes** ↓
- **06** → **Registration**
- **07** → **Parts master data in SAP**
- **08** → **Distribution of release information**

**Right Path:**
- **Release for use**
- **Decision:** Release by standardisation office?
  - **No** → (Return to control)
  - **Yes** ↓
- **06** → **Registration**
- **07** → **Parts master data in SAP**
- **08** → **Distribution of release information**

**Additional Process:**
- **Decision:** Hazardous substance?
  - **No** → (Continue to end)
  - **Yes** ↓
- **09** → **Upload request to ChemScan database**

**End:** Product is available and evaluation documented

### 5.3 General

#### 5.3.1 Aviation Legal Information on Request for Parts and Materials

(1) For every product that is product-relevant (has contact with aviation parts), product approval is required.

(2) The signed request for parts and materials represents proof of product release. The Standardisation Office ensures that the product release is unambiguous and that the requirements of the product approval are communicated to purchasing.

(3) The RRD Manufacturing Laboratory can grant product approvals for products that are used on engines with design responsibility lying with RRD. If the engine responsibility does not lie with RRD, the responsible RR laboratory should be contacted or reference should be made to an existing product approval from this laboratory.

(4) For products that are applied for Part 21, the corresponding Engine Manual is binding. Furthermore, products approved for new manufacture are listed in the MLC104 list. For products that are applied for Part 145, the OMat list can be referenced.

#### 5.3.2 Occupational Safety Information

(1) The requirements of the Hazardous Substances Regulation are binding for all areas in RRD.

(2) Additionally, the requirements of RRTI00032 apply internally at RRD.

#### 5.3.3 Background on Part Numbers in SAP

Released products are created as a data record in the Material Master in SAP so that ordering can take place. For products that require a certificate, settings for Quality Management in SAP are stored by the corresponding RR department.

In the past, separate part numbers were used for Oberursel and Dahlewitz for identical products. Today, one part number can be used for both locations. Duplicate part numbers are deactivated where possible – purchasing should be contacted for this. Here, marking is carried out in the part number list and the request list by the Standardisation Office. Purchasing additionally marks the TKZ in SAP as "not to be used".

#### 5.3.4 Background on Standard Parts and Semi-finished Products

Standard parts and semi-finished products can be components of parts lists and configuration lists. For this, for OU, the creation of the TKZ in PDM is required first and then the transfer to SAP (see also AAW11-10). In case of uncertainties, the applicant or Change Control (Mr. Homm) should be contacted.

### 5.4 Processing of Requests for Parts and Materials

#### 5.4.1 Process Description

**01** - **Standardisation Office receives a "Request for Parts and Materials" for processing**

Various external parts (e.g., general standard parts, semi-finished products, electrical materials, production equipment, transport and packaging materials, auxiliary, operating, energy and other materials) are integrated into a company-specific numbering system (according to Works Standard N0033) for unique identification. Any RRD employee can submit a request for parts and materials (Form T00221) regarding corresponding operational necessity to apply for a part number.

The Standardisation Office checks the uniqueness of the designation (e.g., aerospace material according to LN), existing number assignment, and the necessity of additional numbering.

The request is checked against the following directory for an already existing numbered part or material (double numbering is to be avoided); or for similar parts that seem usable for the application case (part variety). Search in the following list in the columns "Designation / Category" and "Standard short designation / Title" for the corresponding term:

`P:\k-z\Ofs\Dokumentenservice\Verwaltung\Teilenummernvergabe\Teilenummern 0104....xls`

Check the request and associated documents for completeness (see also Instructions T00221-AA -> click symbol at the end of form T00221):

- Product designation
- Purpose / Engine program / Place of use / Area team leaders
- Manufacturer
- Application for aviation parts yes/no
- Product data sheet
- Product approval for products that come into contact with aviation parts
- Safety data sheet (for HS&E-relevant products)
- Approved supplier (for products to be certified according to MSRR documents). Here, purchasing must be contacted to confirm the specified supplier or, if no supplier is specified, to identify one. (The validity of the supplier approval is checked by the laboratory during evaluation, or later by purchasing.)

Optional request fields are 4, 7, 14, 19.

Save all existing documents for the product (technical data sheets, catalog sheets, etc.) as pdf in the respective subfolders of: `P:\k-z\Ofs\Dokumentenservice\TeileundStoffe\`

**Note:** For production aids, "RRT" numbers may already be assigned. Here, the RRT number is mentioned on the request (Field 52), but a TKZ is still assigned solely for the purpose of IRM-internal administration. SAP creation does not occur in this case.

**Note:** If the TKZ is created in SAP for an English or American plant (e.g., "PL05" - this occurs with TKZ beginning with 1000), the data record may have been overwritten. The usability of the existing TKZ should definitely be checked in advance and a new TKZ assigned if necessary.

**02** - **Assignment of the next free part number from the number range 0104....**

Assignment from the following directory (in the following example 01043776):

`P:\k-z\Ofs\Dokumentenservice\Verwaltung\Teilenummernvergabe\Teilenummern 0104....xls`

"N/A" can be used for the technical order number.

**03** - **Request completion according to RRTI00032 and Instructions T00221-AA**

The request is completed according to RRTI00032 and Instructions T00221-AA (documents for the request in paper form are scanned and saved as pdf file).

Saved in the following directory:

`P:\k-z\Ofs\Dokumentenservice\TeileundStoffe\Datei\Verzeichnis.xlsb`

Assign the next free request number there and enter it in Field 1 of the form (T00221). Field 51: Fill in part number.

Enter the request number in the directory (see example "093/2021" here) and link the existing documents (request, data sheet, safety data sheet and approval documents) in columns M to U.

Email message to applicant that the process (with specification of request number, part number and link to directory) has been registered and the approval circulation is being prepared.

**04** - **Preparation of digital approval circulation**

For the circulation, the information required for processing by Environmental Protection, HS&E and the Manufacturing Laboratory is compiled. Processing is carried out either in OU or in DW, according to the place of use. Please note: Mr. Karsten Bartz takes over the environmental protection assessment for both locations.

**Environmental Protection & HS&E:**

For hazardous substances, a current (not older than 2 years), German-language and EU-compliant safety data sheet must be attached to the request.

Please note: a check (Check MLC132) of the safety data sheet must be carried out in advance via Resources and via the Rolls-Royce substance elimination policy checker tool:

Start the tool and then check all substances from the safety data sheet, Section 3, using the CAS number via the corresponding search function. Without a hit, the request follows the usual path. However, if "prohibited/regulated" substances are identified here, the request, together with relevant documentation, must be sent directly to Environmental Protection (karsten.bartz@rolls-royce.com) and to HS&E (hse-newsou@rolls-royce.com or hs-e-teamdw@rolls-royce.com), with the comment "Hit in MLC132". It is then checked in detail what the RR requirements are and whether the substance can be introduced. Only then does sending to UUB for ChemScan evaluation possibly come into question, if the request has not already been rejected at this point by HS&E.

**Manufacturing Laboratory:**

If the product is product-relevant (contact with aviation parts), approval is necessary. For this purpose, research is carried out in the directory history, in MLC104 and in the OMat directory to determine whether the product is already approved or whether an approval specification (CSS, MSRR, or similar) exists for this product group. The result of the research is communicated to the laboratory - e.g.:

- The product is already listed in MLC104.
- The product is not yet listed in MLC104. A CSS already exists for the application of the product. Please indicate whether conformity should be confirmed in advance.
- The product is not yet listed in MLC104. No CSS exists for the application of the product. Please specify an alternative evaluation method (e.g., inquiry to the manufacturer).

If an approval is mentioned by the applicant under Field 18, the correctness of the information should be checked in advance using the above-mentioned lists and communicated to the laboratory if necessary.

If relevant (SDS is available and must be checked), IRM requests the ChemScan evaluation. For this purpose, send email with request (pdf file) and SDS to UUB-Schwan, gefahrstoffmanagement@uub-schwan.de.

As soon as the ChemScan evaluation is available, start the digital approval circulation. For this purpose, the participating departments (Environmental Protection, HS&E, Manufacturing Laboratory) should be provided with both the request for parts and materials and all other documents relevant to each department (data sheets, SDS, ChemScan evaluation, approval, MLC104 or OMat extract, etc.).

**05** - **Digital approval circulation and processing by Environmental Protection, HS&E and Manufacturing Laboratory**

The evaluation documents are sent by email to the corresponding department and approval is granted by means of date and digital signatures.

**Environmental Protection Processing:** is carried out independently of the location by Karsten Bartz (karsten.bartz@rolls-royce.com) as Environmental Protection Officer.

**Evaluation for Oberursel:** GBS / HSE-OU (hse-newsou@rolls-royce.com) takes over the HS&E processing; central recipient in the laboratory (OME-LAB, Manufacturing Laboratory) is Ralph Gross (ralph.gross@rolls-royce.com).

**Evaluation for Dahlewitz:** GBS / HSE-DW (T. Hanf, K. Schmeier, U. Samuels, K. Mahmudov, Inbox: hs-e-teamdw@rolls-royce.com) takes over the HS&E processing; for this purpose, the request and documents are made available in a temporary evaluation folder (folder name is composed, for example, of request number, year, TKZ, designation and product name) under the link:
`\\deberdna-c011a\Projekte\HS&E RRD\public\TEILE_STOFFE_BEARBEITUNG TEMPORÄR`

After completion of the evaluation, the Standardisation Office is informed that the approved request is ready in the exchange folder. RRD-Materials-SPG (rrd-materials-spg@rolls-royce.com) takes over the laboratory processing.

Schedule monitoring of the approval circulation is carried out via the above-mentioned Verzeichnis.xlsb (columns V, W) and documentation of the last processing status (column M).

After the approval circulation has been completed, the request processed by Environmental Protection, HS&E and the Manufacturing Laboratory returns to the Standardisation Office for release.

• Review of information from Environmental Protection – Field 26 (request approval or rejection). A rejection is communicated to the applicant with justification.
• Review of information from HS&E – Field 33 (request approval or rejection). A rejection is communicated to the applicant with justification.
• Review of information from the Manufacturing Laboratory – Fields 39 to 49 (request approval or rejection). A rejection is communicated to the applicant with justification.

**06** - **For release for first order for product approval (Fields 40 to 46)**

**Processing by the Standardisation Office:**

Enter the release for first order for product approval of the request in "Verzeichnis.xlsb":
- Highlight fields A to L with dark green fill color
- Enter date & note "First order" in fields V & W

**Note:** After first order and receipt of the product, the conformity of the delivered goods (delivery documents, certificates, etc.) with the laboratory requirements is checked - if necessary, the product itself is more thoroughly examined by the laboratory - and subsequently the final release for use is granted (for this purpose, the original request is made available to the laboratory again upon request or after receiving notification from goods receipt or from the applicant).

**07** - **For release for use (Fields 47 to 49)**

• Release of the request by the Standardisation Office in Field 50.

Enter the release of the request in "Verzeichnis.xlsb":
- Highlight fields A to L with light green fill color (for rejected requests, use tan fill color)
- Field C: Release "yes" if the request is approved, or "no" if the request is rejected
- Field I: Enter completion date of release or completion date in case of rejection
- Fields M to U: Link approved (or rejected) request and other documents
- Delete fields V & W

If the product is HS&E-relevant (Field 34) and a safety data sheet is available, IRM enters the product into the hazardous substances register – see Section 5.4.3. PPE articles as well as products applied by external companies (e.g., from FS-Plus) are not entered into the register.

The approved original request with all necessary signatures, or a printout with digital signatures, is archived in the corresponding folder (sorted by TKZ).

**Parts master data creation in SAP (see AAW11-10):**

For release for first order for product approval (Fields 40 to 46):
Creation with the following note in the purchasing order text: - RELEASE for FIRST ORDER for PRODUCT APPROVAL -

**08** - **SAP data record creation or update**

Creation or update of the data record based on laboratory requirements, if the product was previously only released for a first order for product approval (the note about "release for first order" must be deleted).

**Note:** An update is carried out by the corresponding department in DW: for products in OU by purchasing (Quy Luu, or as substitute Annett Focke), for products in DW by the department H&B Stoffe RR DW (handbstoffe.rrdahlewitz@rolls-royce.com) (Sandra Fronczyk, or Linett Gohl-Metzing).

For RRT numbers and for requests that only relate to the evaluation of the base material, no SAP creation takes place, but if necessary, an update of the purchasing order text.

For products for which "stock-keeping: no" is indicated on the request (Field 15), the necessity of creating a SAP data record must be clarified by the applicant.

**09** - **Upload request to ChemScan database**

For hazardous substances, or when the product is HS&E-relevant (Field 34) and a safety data sheet has been evaluated by UUB-Schwan, the substance is automatically created in the hazardous substance management tool ChemScan®, together with SDS & ChemScan evaluation, under the corresponding TKZ. After release for use by the Standardisation Office, the approved request is additionally uploaded by IRM into the mentioned database as follows:

- Start tool via login
- Select Substance Register tab:
- Activate filter function:
- Select substance via TKZ:
- Choose detailed view:
- Add attachment:
- Select file or request:
- The request is now assigned to the substance in the database.

**Note:** Upon request, IRM can attach other relevant documents to the created substances at any time.

**10** - **Distribution of release information**

All relevant RRD employees are informed by email about the approved request (first order for product approval, or release for use).

Template emails are to be used according to location, depending on whether with or without SAP creation, or with or without hazardous substances register entries, under the following link:
`P:\k-z\Ofs\Dokumentenservice\TeileundStoffe\Vordruck\`

In addition to the recipients already specified in the template emails, the following are added to CC:
• Applicant, as well as area team leaders according to information under Field 12
• Other persons additionally involved in the evaluation process

#### 5.4.2 Special Features

For requested products that, according to Field 13 of the request, should have no contact with aviation parts, product approval is not required, therefore no laboratory evaluation takes place. Here, only the Standardisation Office sets the cross under Field 39 at "is not required" and adds the note "No evaluation by the Manufacturing Laboratory, as no manufacturing relevance exists" under Field 49. In such cases, release is carried out by the Standardisation Office directly after receiving HS&E approval.

#### 5.4.3 Entry into Hazardous Substances Register

IRM transfers the information from the request, the SDS and the ChemScan evaluation into the RRD hazardous substances register:

Gefahrstoffkataster\Katastersammlung_actual.xlsx

The following columns are filled out (provided the corresponding information is available):

### 5.5 Attachments

Attachment 1: Request for Parts and Materials according to RRTI00032, located at:
"https://rr.fp7k.exostar.com/customers/rollsroyceplc_forumpass/rrd/rrdms/Templates/T00221.pdf"

Attachment 1 – Request for Parts and Materials
Page 1/1

## 6. Applicable Documents

➢ RRTI00032-001: Rolls-Royce Task Instruction Request for Parts and Materials (AfTS) – Initial Review.

➢ RRTI00032-002: Rolls-Royce Task Instruction Request for Parts and Materials (AfTS) – First / Continuous Ordering.

➢ RRTI00032-003: Rolls-Royce Task Instruction Request for Parts and Materials (AfTS) – Product Review.

## 7. Change Record

## 8. Approval



