import fitz  # PyMuPDF
import json
import os
import shutil
from datetime import datetime
import webbrowser
import tempfile

class PDFFormTester:
    def __init__(self, pdf_path, json_path):
        self.pdf_path = pdf_path
        self.json_path = json_path
        self.field_mapping = self.load_field_mapping()
        self.test_results = {}
        
    def load_field_mapping(self):
        """Load the field mapping from JSON file"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_mock_data(self):
        """Generate mock data for testing"""
        return {
            "1": "2025-TEST-001",
            "2a": "Max Mustermann",
            "2b": "01.01.2025",
            "2c": "Entwicklung",
            "2d": "+49 123 456789",
            "3": "Test Chemikalie ABC",
            "4": "EXT-12345",
            "7": "REACH-001",
            "8": "Test Lieferant GmbH",
            "9": "Test Hersteller AG",
            "10": "Verwendung für Prototypentwicklung und Testverfahren",
            "11": "Engine Program X",
            "12a": "Standort München",
            "12b": "Team Engineering",
            "16": "kg",
            "17a": "10",
            "17b": "wöchentlich",
            "17c": "2 kg",
            "18e": "DIN EN 12345",
            "19": "Zusätzliche Erläuterungen zum Test",
            "20": "Verweis auf Antrag 2024-ABC-001",
            "21": "15.02.2025",
            "22a": "Dr. Schmidt",
            "22a1": "05.01.2025",
            "22b": "Dr. Müller",
            "22b1": "06.01.2025",
            "23a1": "ChemVV Kategorie A",
            "23a2": "Sonstige Regelung XYZ",
            "23b1": "ChemVV Kategorie B",
            "23b2": "Weitere Regelung ABC",
            "24a1": "WGK 2",
            "24a2": "UN 1234",
            "24a3": "LGK 3",
            "24b1": "WGK 1",
            "24b2": "UN 5678",
            "24b3": "LGK 2",
            "25a": "Dr. Umwelt",
            "25c": "10.01.2025",
            "31": "Umweltschutz Erläuterungen",
            "32a": "Dr. Sicherheit",
            "32c": "11.01.2025",
            "38": "Arbeitsschutz Erläuterungen",
            "39a": "Grund der Ablehnung",
            "40a": "Labor Team A",
            "40c": "12.01.2025",
            "41a": "90",
            "42a": "Spezial Zertifikat",
            "44a": "OMat-12345",
            "45": "Produktzulassung nach ISO 9001",
            "46": "Lieferantenanforderungen Details",
            "47a": "Labor Team B",
            "47c": "13.01.2025",
            "48a": "Anderes Zertifikat",
            "49": "Weitere Produktzulassungsforderungen",
            "50a": "Normenstelle Team",
            "50c": "14.01.2025",
            "51": "TKZ-98765",
            "52": "Abschließende Erläuterungen"
        }
    
    def get_button_mock_data(self):
        """Generate mock data for button fields (radio/checkbox)"""
        return {
            "5": "Neubedarf",  # Kennzeichnung des Bedarfs
            "6": "Stoff",      # Kennzeichnung des Produkts
            "13": "Ja (Produktzulassung ist erforderlich)",
            "14": "kurzfristig",
            "15a": "Ja",
            "15b": "Nein",
            "18a": "Ja",
            "18b": "Ja",
            "18c": "Nein",
            "18d": "Ja",
            "22a2": "Ja",
            "22b2": "Nein",
            "23a3": "Ja",
            "23a4": "Nein",
            "23a5": "Ja",
            "23a6": "Nein",
            "26": "Genehmigt",
            "27": "Nein",
            "28": "Ja",
            "29": "Nein",
            "30": "Ja",
            "33": "Genehmigt",
            "34": "Ja",
            "35": "Nein",
            "36": "Ja",
            "37": "Nein",
            "39": "erforderlich und vorhanden",
            "41": "Mindesthaltbarkeit",
            "42": "3.1",
            "43": "Nein",
            "44": "bereits eingetragen",
            "48": "nicht erforderlich"
        }
    
    def fill_complete_form(self, custom_data=None):
        """Fill the entire form with mock data and save once"""
        print("=== Filling Complete Form ===")
        
        # Create a temporary copy of the original PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_pdf_path = f"temp_form_{timestamp}.pdf"
        
        print(f"Creating temporary copy: {temp_pdf_path}")
        shutil.copy2(self.pdf_path, temp_pdf_path)
        
        # Get mock data
        text_data = self.get_mock_data()
        button_data = self.get_button_mock_data()
        
        # Allow custom data override
        if custom_data:
            text_data.update(custom_data.get('text', {}))
            button_data.update(custom_data.get('buttons', {}))
        
        # Open temporary PDF for all updates
        doc = fitz.open(temp_pdf_path)
        
        updated_count = 0
        error_count = 0
        
        print(f"Updating {len(text_data)} text fields...")
        # Update all text fields
        for field_id, value in text_data.items():
            if field_id in self.field_mapping:
                try:
                    if self.set_text_field(doc, field_id, value):
                        updated_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    print(f"Error updating text field {field_id}: {e}")
                    error_count += 1
        
        print(f"Updating {len(button_data)} button fields...")
        # Update all button fields
        for field_id, display_value in button_data.items():
            if field_id in self.field_mapping:
                field_info = self.field_mapping[field_id]
                if field_info["type"] == "btn":
                    values = field_info.get("values", {})
                    if display_value in values:
                        pdf_value = values[display_value]
                        try:
                            if self.set_button_field(doc, field_id, pdf_value):
                                updated_count += 1
                            else:
                                error_count += 1
                        except Exception as e:
                            print(f"Error updating button field {field_id}: {e}")
                            error_count += 1
                    else:
                        print(f"Invalid button value for field {field_id}: {display_value}")
                        error_count += 1
        
        # Save the temporary file with incremental save
        print(f"Saving changes to temporary file...")
        doc.saveIncr()
        doc.close()
        
        # Create final output file
        output_path = f"complete_form_{timestamp}.pdf"
        shutil.move(temp_pdf_path, output_path)
        
        # Display result
        self.display_pdf(output_path)
        
        print(f"\n=== Complete Form Fill Results ===")
        print(f"✅ Updated: {updated_count} fields")
        print(f"❌ Errors: {error_count} fields")
        print(f"📄 Original: {self.pdf_path} (preserved)")
        print(f"📄 Output: {output_path}")
        
        return output_path
    
    def test_single_field(self, field_id, test_value=None, keep_file=False):
        """Test a single field with interactive verification"""
        if field_id not in self.field_mapping:
            print(f"Field {field_id} not found in mapping")
            return False
            
        field_info = self.field_mapping[field_id]
        field_name = field_info["name"]
        field_type = field_info["type"]
        
        print(f"\n=== Testing Field {field_id}: {field_name} ===")
        print(f"Type: {field_type}")
        
        # Create temporary copy for testing
        temp_pdf_path = f"temp_test_{field_id}_{datetime.now().strftime('%H%M%S')}.pdf"
        print(f"Creating temporary copy: {temp_pdf_path}")
        shutil.copy2(self.pdf_path, temp_pdf_path)
        
        # Open temporary PDF
        doc = fitz.open(temp_pdf_path)
        
        if field_type == "text":
            # Test text field
            if test_value is None:
                mock_data = self.get_mock_data()
                test_value = mock_data.get(field_id, f"Test value for {field_id}")
            
            print(f"Setting text value: '{test_value}'")
            self.set_text_field(doc, field_id, test_value)
            
        elif field_type == "btn":
            # Test button field (radio/checkbox)
            values = field_info.get("values", {})
            print(f"Available values: {list(values.keys())}")
            
            if test_value is None:
                # Use first available value for testing
                test_value = list(values.keys())[0] if values else None
            
            if test_value and test_value in values:
                print(f"Setting button value: '{test_value}' -> '{values[test_value]}'")
                self.set_button_field(doc, field_id, values[test_value])
            else:
                print(f"Invalid test value: {test_value}")
                return False
                
        elif field_type == "sig":
            print("Signature field - skipping for now")
            doc.close()
            return True
        
        # Save changes to temporary file
        print(f"Saving changes to temporary file...")
        doc.saveIncr()
        doc.close()
        
        # Create final output file
        output_path = f"test_field_{field_id}_{datetime.now().strftime('%H%M%S')}.pdf"
        shutil.move(temp_pdf_path, output_path)
        
        # Open in browser/viewer
        self.display_pdf(output_path)
        
        # Get user feedback
        if field_type == "text":
            response = input(f"Is the text '{test_value}' correctly displayed? (y/n): ").lower()
            result = response == 'y'
        else:
            response = input(f"Is the button value '{test_value}' correctly selected? (y/n): ").lower()
            result = response == 'y'
            
            if not result and field_type == "btn":
                # Let user try other values
                print("Let's try other values:")
                for i, (display_val, pdf_val) in enumerate(values.items()):
                    print(f"{i+1}. {display_val} -> {pdf_val}")
                
                choice = input("Enter number to test (or 'skip'): ")
                if choice.isdigit():
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(values):
                        new_test_value = list(values.keys())[choice_idx]
                        return self.test_single_field(field_id, new_test_value, keep_file)
        
        # Clean up test file unless requested to keep
        if not keep_file and os.path.exists(output_path):
            os.remove(output_path)
        elif keep_file:
            print(f"Kept test file: {output_path}")
            
        self.test_results[field_id] = {
            "field_name": field_name,
            "field_type": field_type,
            "test_value": test_value,
            "result": result
        }
        
        return result
    
    def batch_test_fields(self, field_ids, custom_values=None):
        """Test multiple fields in a single PDF document"""
        print(f"=== Batch Testing {len(field_ids)} Fields ===")
        
        if custom_values is None:
            custom_values = {}
        
        # Create temporary copy for batch testing
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_pdf_path = f"temp_batch_{timestamp}.pdf"
        
        print(f"Creating temporary copy: {temp_pdf_path}")
        shutil.copy2(self.pdf_path, temp_pdf_path)
        
        # Open temporary PDF
        doc = fitz.open(temp_pdf_path)
        
        updated_count = 0
        mock_data = self.get_mock_data()
        button_mock_data = self.get_button_mock_data()
        
        # Update all requested fields
        for field_id in field_ids:
            if field_id not in self.field_mapping:
                print(f"Field {field_id} not found in mapping")
                continue
                
            field_info = self.field_mapping[field_id]
            field_type = field_info["type"]
            
            try:
                if field_type == "text":
                    test_value = custom_values.get(field_id, mock_data.get(field_id, f"Test {field_id}"))
                    if self.set_text_field(doc, field_id, test_value):
                        print(f"✅ Text field {field_id}: '{test_value}'")
                        updated_count += 1
                    else:
                        print(f"❌ Failed to set text field {field_id}")
                        
                elif field_type == "btn":
                    display_value = custom_values.get(field_id, button_mock_data.get(field_id))
                    if display_value:
                        values = field_info.get("values", {})
                        if display_value in values:
                            pdf_value = values[display_value]
                            if self.set_button_field(doc, field_id, pdf_value):
                                print(f"✅ Button field {field_id}: '{display_value}' -> '{pdf_value}'")
                                updated_count += 1
                            else:
                                print(f"❌ Failed to set button field {field_id}")
                        else:
                            print(f"❌ Invalid button value for {field_id}: {display_value}")
                    else:
                        print(f"⏭️ No test value for button field {field_id}")
                        
            except Exception as e:
                print(f"❌ Error updating field {field_id}: {e}")
        
        # Save changes to temporary file
        print(f"\nSaving batch test changes...")
        doc.saveIncr()
        doc.close()
        
        # Create final output file
        output_path = f"batch_test_{timestamp}.pdf"
        shutil.move(temp_pdf_path, output_path)
        
        # Display result
        self.display_pdf(output_path)
        
        print(f"\n=== Batch Test Results ===")
        print(f"✅ Updated: {updated_count} fields")
        print(f"📄 Original: {self.pdf_path} (preserved)")
        print(f"📄 Output: {output_path}")
        
        return output_path
    
    def set_text_field(self, doc, field_id, value):
        """Set text field value"""
        try:
            # Try different possible field names
            possible_names = [
                field_id,
                f"field_{field_id}",
                f"Field{field_id}",
                self.field_mapping[field_id]["name"]
            ]
            
            for page in doc:
                for widget in page.widgets():
                    if widget.field_name in possible_names:
                        widget.field_value = str(value)
                        widget.update()
                        print(f"Set field '{widget.field_name}' to '{value}'")
                        return True
            
            print(f"Warning: Could not find text field for {field_id}")
            return False
            
        except Exception as e:
            print(f"Error setting text field {field_id}: {e}")
            return False
    
    def set_button_field(self, doc, field_id, pdf_value):
        """Set button field value (radio/checkbox)"""
        try:
            possible_names = [
                field_id,
                f"field_{field_id}",
                f"Field{field_id}",
                self.field_mapping[field_id]["name"]
            ]
            
            for page in doc:
                for widget in page.widgets():
                    if widget.field_name in possible_names:
                        widget.field_value = pdf_value
                        widget.update()
                        print(f"Set button field '{widget.field_name}' to '{pdf_value}'")
                        return True
            
            print(f"Warning: Could not find button field for {field_id}")
            return False
            
        except Exception as e:
            print(f"Error setting button field {field_id}: {e}")
            return False
    
    def display_pdf(self, pdf_path):
        """Display PDF file"""
        abs_path = os.path.abspath(pdf_path)
        print(f"Opening PDF: {abs_path}")
        
        try:
            # Try to open with default system viewer
            if os.name == 'nt':  # Windows
                os.startfile(abs_path)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{abs_path}"')
        except Exception as e:
            print(f"Could not open PDF automatically: {e}")
            print(f"Please manually open: {abs_path}")
    
    def test_all_fields(self):
        """Test all fields interactively"""
        print("=== PDF Form Field Testing ===")
        print(f"PDF: {self.pdf_path}")
        print(f"Mapping: {self.json_path}")
        print(f"Total fields: {len(self.field_mapping)}")
        
        for field_id in sorted(self.field_mapping.keys()):
            try:
                result = self.test_single_field(field_id)
                print(f"Field {field_id}: {'PASS' if result else 'FAIL'}")
            except KeyboardInterrupt:
                print("\nTesting interrupted by user")
                break
            except Exception as e:
                print(f"Error testing field {field_id}: {e}")
                self.test_results[field_id] = {
                    "field_name": self.field_mapping[field_id]["name"],
                    "error": str(e)
                }
        
        self.save_test_results()
    
    def test_specific_fields(self, field_ids):
        """Test specific fields"""
        for field_id in field_ids:
            if field_id in self.field_mapping:
                self.test_single_field(field_id)
            else:
                print(f"Field {field_id} not found in mapping")
    
    def save_test_results(self):
        """Save test results to JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\nTest results saved to: {results_file}")
        
        # Print summary
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results.values() if r.get('result', False))
        print(f"Summary: {passed}/{total} fields passed")
    
    def cleanup_temp_files(self):
        """Clean up temporary files created during testing"""
        temp_patterns = [
            "temp_*.pdf",
            "test_field_*.pdf",
            "complete_form_*.pdf",
            "batch_test_*.pdf"
        ]
        
        cleaned_count = 0
        for pattern in temp_patterns:
            import glob
            for file_path in glob.glob(pattern):
                try:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"Could not remove {file_path}: {e}")
        
        print(f"Cleaned up {cleaned_count} temporary files")

def main():
    """Main function with interactive menu"""
    pdf_path = "pdf.pdf"
    json_path = "pdf_dict.json"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    if not os.path.exists(json_path):
        print(f"Error: JSON mapping file not found: {json_path}")
        return
    
    tester = PDFFormTester(pdf_path, json_path)
    
    while True:
        print("\n=== PDF Form Tester ===")
        print("1. Fill complete form (all fields at once)")
        print("2. Test specific field")
        print("3. Batch test multiple fields")
        print("4. Test button fields only")
        print("5. Test text fields only")
        print("6. Test all fields individually")
        print("7. Clean up temporary files")
        print("8. Exit")
        
        choice = input("Enter your choice (1-8): ")
        
        if choice == "1":
            tester.fill_complete_form()
        elif choice == "2":
            field_id = input("Enter field ID to test: ")
            tester.test_single_field(field_id, keep_file=True)
        elif choice == "3":
            field_ids_str = input("Enter field IDs (comma-separated): ")
            field_ids = [fid.strip() for fid in field_ids_str.split(',')]
            tester.batch_test_fields(field_ids)
        elif choice == "4":
            button_fields = [fid for fid, info in tester.field_mapping.items() 
                           if info["type"] == "btn"]
            print(f"Batch testing {len(button_fields)} button fields...")
            tester.batch_test_fields(button_fields)
        elif choice == "5":
            text_fields = [fid for fid, info in tester.field_mapping.items() 
                          if info["type"] == "text"]
            print(f"Batch testing {len(text_fields)} text fields...")
            tester.batch_test_fields(text_fields)
        elif choice == "6":
            tester.test_all_fields()
        elif choice == "7":
            tester.cleanup_temp_files()
        elif choice == "8":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
