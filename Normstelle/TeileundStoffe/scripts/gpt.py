import base64
import json
import PyPDF2
import fitz  # PyMuPDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.x509 import load_pem_x509_certificate


# Function to extract signature information from the PDF
def extract_signature_from_pdf(pdf_file_path):
    # Open PDF using PyMuPDF (fitz)
    pdf_document = fitz.open(pdf_file_path)
    
    # Loop through each page and check for embedded signature field
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        widgets = page.widgets()  # Get all form fields/widgets
        for widget in widgets:
            if widget.field_name == "Signature":  # You may need to adapt this to your PDF signature field name
                signature = widget.get_text("text")  # Retrieve the signature data (text form)
                signature_info = widget.field_value  # Embedded signature data in field_value
                return signature_info  # Return signature data if found
    return None

# Function to validate the digital signature
def validate_signature(signature_bytes, original_data, public_key_pem):
    try:
        # Load public key
        public_key = serialization.load_pem_public_key(public_key_pem)

        # Hash the original document data (the original data you want to verify the signature against)
        document_hash = hashes.Hash(hashes.SHA256())
        document_hash.update(original_data)
        document_digest = document_hash.finalize()

        # Verify the signature
        public_key.verify(
            signature_bytes,
            document_digest,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print("Signature is valid.")
    except Exception as e:
        print("Signature is invalid:", e)

# Extract the original document content (e.g., from a PDF file) that was signed
def extract_pdf_content(pdf_file_path):
    with open(pdf_file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        # Assuming the document is in the first page
        page = reader.pages[0]
        return page.extract_text()

# Example of getting the public key (replace this with the actual public key associated with the signature)
public_key_pem = b"""
-----BEGIN PUBLIC KEY-----
<Your public key here>
-----END PUBLIC KEY-----
"""

# PDF path
pdf_path = "signed_document.pdf"

# Extract the signature from the PDF
signature_bytes = extract_signature_from_pdf(pdf_path)

if signature_bytes:
    # Extract original content from the PDF
    original_pdf_content = extract_pdf_content(pdf_path)

    # Validate the signature with the original PDF content
    validate_signature(signature_bytes, original_pdf_content.encode(), public_key_pem)
else:
    print("No signature found in the PDF.")
