#!/usr/bin/env python3
import json
import os
import sys
import glob
from datetime import datetime
from pathlib import Path
import hashlib

class TemplateDatabase:
    def __init__(self, db_path="template_database.json"):
        self.db_path = db_path
        self.database = self.load_database()
    
    def load_database(self):
        """Load existing template database or create new one"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load database {self.db_path}: {e}")
                return self.create_empty_database()
        else:
            return self.create_empty_database()
    
    def create_empty_database(self):
        """Create empty database structure"""
        return {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'templates': {},
            'statistics': {
                'total_templates': 0,
                'total_pdfs_processed': 0
            }
        }
    
    def save_database(self):
        """Save database to file"""
        self.database['last_updated'] = datetime.now().isoformat()
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.database, f, indent=2, ensure_ascii=False, default=str)
            print(f"Database saved to {self.db_path}")
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def extract_pdf_data(self, pdf_path):
        """Extract data from PDF using the extractor"""
        import subprocess
        try:
            result = subprocess.run([
                sys.executable, 'extractor.py', pdf_path
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                raise Exception(f"Extractor failed: {result.stderr}")
        except Exception as e:
            raise Exception(f"Failed to extract from {pdf_path}: {e}")
    
    def add_template(self, pdf_path, template_name=None, description=""):
        """Add a new template to the database"""
        print(f"Processing template: {pdf_path}")
        
        try:
            # Extract PDF data
            pdf_data = self.extract_pdf_data(pdf_path)
            
            # Generate template name if not provided
            if not template_name:
                template_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            # Get signature hash for template ID
            signature_hash = pdf_data.get('template_signature', {}).get('signature_hash', 'unknown')
            
            # Create template entry
            template_entry = {
                'name': template_name,
                'description': description,
                'signature_hash': signature_hash,
                'sample_file': pdf_path,
                'added_date': datetime.now().isoformat(),
                'extraction_data': pdf_data,
                'identification_keys': self.generate_identification_keys(pdf_data),
                'statistics': {
                    'matches_found': 0,
                    'last_match': None
                }
            }
            
            # Add to database
            template_id = f"template_{len(self.database['templates']) + 1:03d}"
            self.database['templates'][template_id] = template_entry
            self.database['statistics']['total_templates'] += 1
            
            print(f"Added template '{template_name}' with ID: {template_id}")
            print(f"Signature hash: {signature_hash}")
            
            return template_id
            
        except Exception as e:
            print(f"Error adding template {pdf_path}: {e}")
            return None
    
    def generate_identification_keys(self, pdf_data):
        """Generate key identifiers for quick template matching"""
        keys = {
            'form_field_names': [],
            'static_text_patterns': [],
            'structure_signature': '',
            'metadata_signature': ''
        }
        
        # Form field names (very reliable)
        if 'form_fields' in pdf_data:
            field_names = [f['name'] for f in pdf_data['form_fields']['fields']]
            keys['form_field_names'] = sorted(field_names)
        
        # Static text patterns (template labels/headers)
        if 'text' in pdf_data:
            patterns = []
            for pattern in pdf_data['text']['text_patterns'].keys():
                if (len(pattern) > 10 and 
                    len(pattern.split()) > 1 and
                    not any(char.isdigit() for char in pattern[-10:])):  # Avoid patterns with trailing numbers
                    patterns.append(pattern)
            keys['static_text_patterns'] = sorted(patterns[:10])  # Top 10 patterns
        
        # Structure signature
        if 'structure' in pdf_data:
            struct = pdf_data['structure']
            struct_sig = f"{struct['page_count']}p_{struct['total_text_blocks']}t_{struct['total_drawings']}d"
            keys['structure_signature'] = struct_sig
        
        # Metadata signature
        if 'metadata' in pdf_data:
            meta_parts = []
            for source in ['fitz', 'pypdf']:
                if source in pdf_data['metadata']:
                    creator = pdf_data['metadata'][source].get('creator', '').strip()
                    producer = pdf_data['metadata'][source].get('producer', '').strip()
                    if creator:
                        meta_parts.append(creator)
                    if producer:
                        meta_parts.append(producer)
            keys['metadata_signature'] = '|'.join(meta_parts)
        
        return keys
    
    def find_matching_template(self, pdf_path):
        """Find matching template for a given PDF"""
        print(f"Searching for template match: {pdf_path}")
        
        try:
            # Extract PDF data
            pdf_data = self.extract_pdf_data(pdf_path)
            test_keys = self.generate_identification_keys(pdf_data)
            
            best_match = None
            best_score = 0.0
            
            # Compare against all templates
            for template_id, template in self.database['templates'].items():
                score = self.calculate_match_score(test_keys, template['identification_keys'])
                
                if score > best_score:
                    best_score = score
                    best_match = {
                        'template_id': template_id,
                        'template_name': template['name'],
                        'score': score,
                        'signature_hash': template['signature_hash']
                    }
            
            # Update match statistics
            if best_match and best_score > 0.7:
                template_id = best_match['template_id']
                self.database['templates'][template_id]['statistics']['matches_found'] += 1
                self.database['templates'][template_id]['statistics']['last_match'] = datetime.now().isoformat()
            
            return best_match, best_score
            
        except Exception as e:
            print(f"Error finding template match: {e}")
            return None, 0.0
    
    def calculate_match_score(self, keys1, keys2):
        """Calculate match score between two sets of identification keys"""
        total_score = 0.0
        total_weight = 0.0
        
        # Form field names (highest weight)
        field_score = self.compare_lists(keys1['form_field_names'], keys2['form_field_names'])
        total_score += field_score * 0.5
        total_weight += 0.5
        
        # Static text patterns
        text_score = self.compare_lists(keys1['static_text_patterns'], keys2['static_text_patterns'])
        total_score += text_score * 0.3
        total_weight += 0.3
        
        # Structure signature
        if keys1['structure_signature'] and keys2['structure_signature']:
            struct_score = 1.0 if keys1['structure_signature'] == keys2['structure_signature'] else 0.0
            total_score += struct_score * 0.15
            total_weight += 0.15
        
        # Metadata signature
        if keys1['metadata_signature'] and keys2['metadata_signature']:
            meta_score = 1.0 if keys1['metadata_signature'] == keys2['metadata_signature'] else 0.0
            total_score += meta_score * 0.05
            total_weight += 0.05
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def compare_lists(self, list1, list2):
        """Compare two lists and return similarity score"""
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        set1 = set(list1)
        set2 = set(list2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def list_templates(self):
        """List all templates in the database"""
        if not self.database['templates']:
            print("No templates in database.")
            return
        
        print(f"\nTemplate Database ({self.database['statistics']['total_templates']} templates):")
        print("-" * 80)
        
        for template_id, template in self.database['templates'].items():
            print(f"ID: {template_id}")
            print(f"Name: {template['name']}")
            print(f"Description: {template['description']}")
            print(f"Sample file: {template['sample_file']}")
            print(f"Form fields: {len(template['identification_keys']['form_field_names'])}")
            print(f"Matches found: {template['statistics']['matches_found']}")
            print(f"Added: {template['added_date']}")
            print("-" * 40)
    
    def export_template(self, template_id, output_path):
        """Export template data to separate file"""
        if template_id not in self.database['templates']:
            print(f"Template {template_id} not found.")
            return False
        
        template = self.database['templates'][template_id]
        
        export_data = {
            'template_id': template_id,
            'export_date': datetime.now().isoformat(),
            'template_data': template
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            print(f"Template {template_id} exported to {output_path}")
            return True
        except Exception as e:
            print(f"Error exporting template: {e}")
            return False

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python template_database.py add <pdf_file> [template_name] [description]")
        print("  python template_database.py add_batch <pdf_directory>")
        print("  python template_database.py find <pdf_file>")
        print("  python template_database.py list")
        print("  python template_database.py export <template_id> <output_file>")
        print("\nExamples:")
        print("  python template_database.py add form1.pdf 'Application Form' 'Standard application form'")
        print("  python template_database.py add_batch ./pdf_templates/")
        print("  python template_database.py find unknown_form.pdf")
        sys.exit(1)
    
    db = TemplateDatabase()
    command = sys.argv[1].lower()
    
    if command == 'add':
        if len(sys.argv) < 3:
            print("Error: PDF file required")
            sys.exit(1)
        
        pdf_file = sys.argv[2]
        template_name = sys.argv[3] if len(sys.argv) > 3 else None
        description = sys.argv[4] if len(sys.argv) > 4 else ""
        
        if not os.path.exists(pdf_file):
            print(f"Error: File {pdf_file} not found")
            sys.exit(1)
        
        template_id = db.add_template(pdf_file, template_name, description)
        if template_id:
            db.save_database()
    
    elif command == 'add_batch':
        if len(sys.argv) < 3:
            print("Error: Directory required")
            sys.exit(1)
        
        pdf_dir = sys.argv[2]
        if not os.path.isdir(pdf_dir):
            print(f"Error: Directory {pdf_dir} not found")
            sys.exit(1)
        
        pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {pdf_dir}")
            sys.exit(1)
        
        print(f"Found {len(pdf_files)} PDF files")
        added_count = 0
        
        for pdf_file in pdf_files:
            print(f"\nProcessing {pdf_file}...")
            template_id = db.add_template(pdf_file)
            if template_id:
                added_count += 1
        
        print(f"\nAdded {added_count} templates to database")
        db.save_database()
    
    elif command == 'find':
        if len(sys.argv) < 3:
            print("Error: PDF file required")
            sys.exit(1)
        
        pdf_file = sys.argv[2]
        if not os.path.exists(pdf_file):
            print(f"Error: File {pdf_file} not found")
            sys.exit(1)
        
        match, score = db.find_matching_template(pdf_file)
        
        result = {
            'query_file': pdf_file,
            'match_found': match is not None,
            'match_score': score,
            'match_details': match,
            'threshold': 0.7
        }
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == 'list':
        db.list_templates()
    
    elif command == 'export':
        if len(sys.argv) < 4:
            print("Error: Template ID and output file required")
            sys.exit(1)
        
        template_id = sys.argv[2]
        output_file = sys.argv[3]
        
        db.export_template(template_id, output_file)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 