ATS Workflow

This outlines some processing procedures for a approval workflow of consumables and materials application requests. This should combine automated tasks and workflow with human
verification and intervention.

1. Incoming Emails from Applicants
- We monitor outlook inbox, so emails could be any category, we need to parse and identify only ATS related emails, if they are a new application or related to a existing application.
- Email must contain these informations: 
    - Subject contains one of: "Antrag", "ATS", "AfTS", 
    - Attachment contains:
        - Application form pdf (has a known structure), needs to be newest version 
        - MSDS and TDS/PDS (by parsing the text)
        - MSDS needs to be in german, needs to be not less than 2 years old (parse for text and dates)
        - other documents, like certification documents/extrations (COC)

2. Application assessment
- We need to create a score-like feature that judges the emails for fitness to ATS 
    - And one for completeness of the application based on these factors
        - All required Application form fields filled
        - If attachments are checked, email must contain those (either SDS, TDS/PDS, COC)
        - Based on missing information, we generate a email template to the applicant to provide missing information
        - For example:
        - Applicant sends ATS Email with outdated Application form, missing fields and missing attachments
        - We generate a email based on a template that lists these issues (we have a mapping of issues to strings):
            - Please use the new version of the application form for future applications (then attach the new form)
            - Please provide information about these fields:
                - Field 15: Should we order via SAP?
                - Field 18: You checked attachments, but didnt include any in the email. Please provide the documents.
        - This should assist us in judging and processing the applications.

3. Post-application processing
3.1. Parsing of Application form

- We parse the form fields of the application pdf to extract all relevant information
- We parse the attachments for information, such as SDS language, date etc. 
- Assigment of IDs: Antragsnummer (Application-ID) and TKZ (Teilekennzahl (PN)), these are serial numbers, assigned FIFO progressively to each ATS



4. Approval Circulation

- After registration of the application, it undergoes a approval circle to different departments. The application form 
and relevant attachments are sent to these departments:

1. UUB (Rechts- und Gefährdungsbeurteilung - registration of hazardous chemicals into a database - assesses the risk and legal considerations for chemicals)
2. UWS (Umweltschutz - Environment protection department - assesses environmental concerns for chemicals)
3. HSE (Arbeits- und Gesundheitsschutz - Health and Safety - assesses human health and safety for handling chemicals)
4. LAB (Fertigungslabor - Manufacturing/Materials Laboratory. - assesses manufacturing concerns for materials interacting with chemicals)

- We as standartization office manage the approval workflow. So after applicant sent the application, we check it, and send it to UUB,
which returns to us the application, filled out with their fields, and we check it, and send it to the next one and so on.

- Certain departments only need certain documents:
0. Applicant _ -> ATS, SDS/PDS, COC
1. UUB (ATS, SDS/PDS) -> ATS_UUB, CS (ChemScan)
2. UWS (ATS_UUB, SDS/PDS, CS) -> ATS_UWS
3. HSE (ATS_UWS, SDS/PDS, CS) - ATS_HSE
4. LAB (ATS_HSE, CS)

5. Old infrastructure
- All of this is currently done with these tools:
- Outlook, Excel, SAP
- Goal is to automate most of it as much as possible, especially management of application and its documents



