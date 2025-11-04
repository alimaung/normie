"""
CMSR Automation - Main Workflow Module

Workflow automation for incoming CMSR (Consumable Material Supply Request)

This module integrates all components:
- PDF processing (pdf_processor.py)
- ID generation (id_generator.py) 
- Excel writing (excel_writer.py)

Usage:
    python main_workflow.py path/to/pdf_file.pdf
"""

from pathlib import Path
import sys
from pdf_processor import process_pdf_for_excel
from id_generator import generate_new_ids
from excel_writer import write_to_excel_sheets

def process_cmsr_application(pdf_path, tkz_file_path=r"Q:\DocumentManagement\NormstelleShare\Teilenummernvergabe\Teilenummern_0104....xls", verzeichnis_file_path=r"Q:\DocumentManagement\NormstelleShare\TeileundStoffe\Datei\Verzeichnis - Copy.xlsb"):
    """
    Complete CMSR processing workflow.
    
    Args:
        pdf_path: Path to the PDF application form
        tkz_file_path: Path to TKZ.xls file (optional, auto-detected if None)
        verzeichnis_file_path: Path to Verzeichnis.xlsb file (optional, auto-detected if None)
    
    Returns:
        dict: Processing result with success status and generated IDs
    """
    
    print("=== CMSR Application Processing ===")
    print(f"Processing PDF: {pdf_path}")
    
    # Convert all paths to Path objects for consistent handling
    pdf_path = Path(pdf_path)
    
    # Set default file paths if not provided
    if tkz_file_path is None:
        tkz_file_path = Path(__file__).parent / "TKZ.xls"
    else:
        tkz_file_path = Path(tkz_file_path)
        
    if verzeichnis_file_path is None:
        verzeichnis_file_path = Path(__file__).parent / "Verzeichnis.xlsb"
    else:
        verzeichnis_file_path = Path(verzeichnis_file_path)
    
    # Validate input files exist
    if not pdf_path.exists():
        return {"success": False, "error": f"PDF file not found: {pdf_path}"}
    
    if not tkz_file_path.exists():
        return {"success": False, "error": f"TKZ file not found: {tkz_file_path}"}
        
    if not verzeichnis_file_path.exists():
        return {"success": False, "error": f"Verzeichnis file not found: {verzeichnis_file_path}"}
    
    try:
        # Step 1: Process PDF and extract form data
        print("\n--- Step 1: PDF Processing ---")
        pdf_data = process_pdf_for_excel(pdf_path)
        
        if not pdf_data:
            return {"success": False, "error": "Failed to process PDF or not a Neubedarf"}
        
        # Step 2: Generate new IDs
        print("\n--- Step 2: ID Generation ---")
        new_tkz, new_antragsnummer = generate_new_ids(tkz_file_path, verzeichnis_file_path)
        
        # Step 3: Write to Excel sheets
        print("\n--- Step 3: Excel Writing ---")
        excel_success = write_to_excel_sheets(
            pdf_data, 
            new_tkz, 
            new_antragsnummer, 
            tkz_file_path, 
            verzeichnis_file_path
        )
        
        if not excel_success:
            return {
                "success": False, 
                "error": "Failed to write to Excel sheets",
                "tkz": new_tkz,
                "antragsnummer": new_antragsnummer
            }
        
        # Success!
        result = {
            "success": True,
            "tkz": new_tkz,
            "antragsnummer": new_antragsnummer,
            "pdf_fields_processed": len(pdf_data),
            "message": f"Successfully processed CMSR application. Generated TKZ: {new_tkz}, Antragsnummer: {new_antragsnummer}"
        }
        
        print(f"\n=== SUCCESS ===")
        print(f"Generated TKZ: {new_tkz}")
        print(f"Generated Antragsnummer: {new_antragsnummer}")
        print(f"Processed {len(pdf_data)} PDF fields")
        
        return result
        
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def main():
    """
    Command line interface for CMSR processing.
    """
    if len(sys.argv) != 2:
        print("Usage: python main_workflow.py <pdf_file_path>")
        print("Example: python main_workflow.py ../pdfparser/Antrag_T&S_Huby_Swab_Wattestäbchen.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    result = process_cmsr_application(pdf_path)
    
    if result["success"]:
        print(f"\n✓ {result['message']}")
        sys.exit(0)
    else:
        print(f"\n✗ Error: {result['error']}")
        sys.exit(1)

# Test function for development
def test_workflow():
    """
    Test the workflow with the sample PDF file.
    """
    print("=== Testing CMSR Workflow ===")
    
    # Test with the sample PDF
    test_pdf = Path(__file__).parent.parent / "pdfparser" / "Antrag T&S Huby Swab Wattestäbchen.pdf"
    
    if not test_pdf.exists():
        print(f"Test PDF not found: {test_pdf}")
        return False
    
    result = process_cmsr_application(test_pdf)
    
    print(f"\nTest Result: {'SUCCESS' if result['success'] else 'FAILED'}")
    if result['success']:
        print(f"Generated TKZ: {result['tkz']}")
        print(f"Generated Antragsnummer: {result['antragsnummer']}")
    else:
        print(f"Error: {result['error']}")
    
    return result['success']

if __name__ == "__main__":
    # If called with 'test' argument, run test mode
    if len(sys.argv) == 2 and sys.argv[1] == "test":
        test_workflow()
    else:
        main()
