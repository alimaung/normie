#!/usr/bin/env python3
import json
import sys
import os
import re
from difflib import SequenceMatcher
from collections import defaultdict
from datetime import datetime

# Import the simple text extractor
from simple_text_extractor import extract_text_simple

class PDFTemplateComparer:
    def __init__(self, template_file="extracted_text.json"):
        self.template_file = template_file
        self.template_data = self.load_template()
        
    def detect_encoding(self, file_path):
        """Detect file encoding by examining BOM and content"""
        with open(file_path, 'rb') as f:
            raw_data = f.read(4)
        
        # Check for BOM (Byte Order Mark)
        if raw_data.startswith(b'\xff\xfe\x00\x00'):
            return 'utf-32-le'
        elif raw_data.startswith(b'\x00\x00\xfe\xff'):
            return 'utf-32-be'
        elif raw_data.startswith(b'\xff\xfe'):
            return 'utf-16-le'
        elif raw_data.startswith(b'\xfe\xff'):
            return 'utf-16-be'
        elif raw_data.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-sig'
        else:
            return 'utf-8'

    def load_template(self):
        """Load the reference template data"""
        if not os.path.exists(self.template_file):
            raise FileNotFoundError(f"Template file {self.template_file} not found")
        
        # Check file size first
        file_size = os.path.getsize(self.template_file)
        if file_size == 0:
            raise Exception(f"Template file {self.template_file} is empty")
        
        # Detect encoding first
        detected_encoding = self.detect_encoding(self.template_file)
        print(f"Detected encoding: {detected_encoding}")
        
        # Try different encodings for the template file (including UTF-16 variants)
        # Put detected encoding first in the list
        encodings = [detected_encoding, 'utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        # Remove duplicates while preserving order
        encodings = list(dict.fromkeys(encodings))
        last_error = None
        
        for encoding in encodings:
            try:
                with open(self.template_file, 'r', encoding=encoding) as f:
                    content = f.read()
                    if not content.strip():
                        raise Exception(f"Template file {self.template_file} is empty or contains only whitespace")
                    
                    # Reset file pointer and load JSON
                    f.seek(0)
                    data = json.load(f)
                    print(f"Successfully loaded template with encoding: {encoding}")
                    return data
                    
            except UnicodeDecodeError as e:
                last_error = f"Encoding {encoding}: {e}"
                continue
            except json.JSONDecodeError as e:
                last_error = f"JSON decode error with {encoding}: {e}"
                continue
        
        # If all fail, try with error replacement and detailed debugging
        try:
            with open(self.template_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                print(f"File content preview (first 100 chars): {repr(content[:100])}")
                
                if not content.strip():
                    raise Exception(f"Template file {self.template_file} is empty or contains only whitespace")
                
                # Try to parse JSON
                f.seek(0)
                data = json.load(f)
                print("Successfully loaded template with UTF-8 error replacement")
                return data
                
        except json.JSONDecodeError as e:
            # Read as bytes to check for BOM or other issues
            with open(self.template_file, 'rb') as f:
                raw_bytes = f.read(50)
                print(f"Raw file start (first 50 bytes): {raw_bytes}")
            
            raise Exception(f"Could not parse JSON in {self.template_file}. Last error: {last_error}, JSON error: {e}")
        except Exception as e:
            raise Exception(f"Could not load template file {self.template_file}: {e}")
    
    def normalize_german_text(self, text):
        """Normalize German text by fixing common encoding issues"""
        replacements = {
            'fⁿr': 'für',
            'ⁿber': 'über', 
            'Σ': 'ä',
            'σ': 'ö',
            'ⁿ': 'ü',
            '▀': 'ß',
            '╝': '%',
            '╓': 'Ö',
            '÷': 'ö',
            'mⁿssen': 'müssen',
            'GefΣhrdung': 'Gefährdung',
            'ErlΣuterung': 'Erläuterung',
            'HΣufigkeit': 'Häufigkeit',
            'AntrΣge': 'Anträge',
            'EinschrΣnkung': 'Einschränkung',
            'BedarfsΣnderung': 'Bedarfsänderung',
            'gemΣ▀': 'gemäß'
        }
        
        normalized = text
        for wrong, correct in replacements.items():
            normalized = normalized.replace(wrong, correct)
        
        return normalized
    
    def extract_pdf_data(self, pdf_path):
        """Extract data from PDF using simple text extractor directly"""
        try:
            # Call the extract function directly instead of subprocess
            return extract_text_simple(pdf_path)
        except Exception as e:
            raise Exception(f"Failed to extract from {pdf_path}: {e}")
    
    def extract_version_info(self, text_lines):
        """Extract version information from text lines"""
        version_info = {
            'document_id': None,
            'version_date': None,
            'version_pattern': None,
            'is_latest': False,
            'matches': []
        }
        
        # Pattern for T00221:YYYY-MM-DD format
        version_pattern = r'T00221:(\d{4}-\d{2}-\d{2})'
        
        for i, line in enumerate(text_lines):
            # Normalize the line first
            normalized_line = self.normalize_german_text(line)
            
            match = re.search(version_pattern, normalized_line)
            if match:
                version_info['document_id'] = 'T00221'
                version_info['version_date'] = match.group(1)
                version_info['version_pattern'] = match.group(0)
                
                # Check if this is the latest known version (2025-05-07)
                if match.group(1) == '2025-05-07':
                    version_info['is_latest'] = True
                
                version_info['matches'].append({
                    'line_index': i,
                    'original_line': line,
                    'normalized_line': normalized_line,
                    'pattern': match.group(0)
                })
        
        return version_info
    
    def calculate_text_similarity(self, template_lines, test_lines):
        """Calculate similarity between template and test text lines"""
        # Normalize both sets of lines
        template_normalized = [self.normalize_german_text(line) for line in template_lines]
        test_normalized = [self.normalize_german_text(line) for line in test_lines]
        
        # Remove empty lines
        template_filtered = [line for line in template_normalized if line.strip()]
        test_filtered = [line for line in test_normalized if line.strip()]
        
        if not template_filtered or not test_filtered:
            return {}
        
        # Calculate different similarity metrics
        scores = {}
        
        # 1. Exact line matches
        template_set = set(template_filtered)
        test_set = set(test_filtered)
        intersection = template_set & test_set
        union = template_set | test_set
        
        scores['exact_line_match'] = len(intersection) / len(union) if union else 0.0
        
        # 2. Sequence similarity using difflib
        matcher = SequenceMatcher(None, template_filtered, test_filtered)
        scores['sequence_similarity'] = matcher.ratio()
        
        # 3. Key phrase matching (form labels, headers)
        template_key_phrases = self.extract_key_phrases(template_filtered)
        test_key_phrases = self.extract_key_phrases(test_filtered)
        
        key_intersection = template_key_phrases & test_key_phrases
        key_union = template_key_phrases | test_key_phrases
        scores['key_phrase_match'] = len(key_intersection) / len(key_union) if key_union else 0.0
        
        # 4. Structure similarity (numbered items, patterns)
        template_structure = self.extract_structure_patterns(template_filtered)
        test_structure = self.extract_structure_patterns(test_filtered)
        
        struct_intersection = template_structure & test_structure
        struct_union = template_structure | test_structure
        scores['structure_match'] = len(struct_intersection) / len(struct_union) if struct_union else 0.0
        
        return scores
    
    def extract_key_phrases(self, lines):
        """Extract key phrases that are likely to be form labels or headers"""
        key_phrases = set()
        
        for line in lines:
            line = line.strip()
            
            # Skip very short lines
            if len(line) < 3:
                continue
            
            # Look for numbered items (form fields)
            if re.match(r'^\d+[a-z]?\s', line):
                key_phrases.add(line)
            
            # Look for section headers
            elif any(keyword in line.lower() for keyword in ['antrag', 'chemscan', 'umweltschutz', 'gesundheit', 'normstelle']):
                key_phrases.add(line)
            
            # Look for field labels ending with ':'
            elif line.endswith(':'):
                key_phrases.add(line)
            
            # Look for specific patterns
            elif any(pattern in line for pattern in ['Rolls-Royce', 'Deutschland', 'RRTI', 'Seite', 'von']):
                key_phrases.add(line)
        
        return key_phrases
    
    def extract_structure_patterns(self, lines):
        """Extract structural patterns from text"""
        patterns = set()
        
        for line in lines:
            line = line.strip()
            
            # Numbered items pattern
            if re.match(r'^\d+[a-z]?\s', line):
                patterns.add(f"numbered_item_{re.match(r'^(\d+[a-z]?)', line).group(1)}")
            
            # Yes/No patterns
            if line in ['ja', 'nein']:
                patterns.add('yes_no_option')
            
            # Signature patterns
            if 'SIGN' in line:
                patterns.add('signature_field')
            
            # Page references
            if 'Seite' in line and 'von' in line:
                patterns.add('page_reference')
            
            # Section headers
            if line.startswith('(') and line.endswith(')'):
                patterns.add('parenthetical_reference')
        
        return patterns
    
    def calculate_overall_score(self, similarity_scores, version_match, structure_match):
        """Calculate overall template match score"""
        weights = {
            'exact_line_match': 0.3,
            'sequence_similarity': 0.2,
            'key_phrase_match': 0.3,
            'structure_match': 0.2
        }
        
        # Base similarity score
        base_score = sum(similarity_scores[metric] * weight for metric, weight in weights.items())
        
        # Version bonus/penalty
        version_bonus = 0.0
        if version_match['has_version']:
            if version_match['is_t00221']:
                version_bonus += 0.1  # 10% bonus for correct document type
            if version_match['is_latest']:
                version_bonus += 0.05  # 5% bonus for latest version
        
        # Structure bonus
        structure_bonus = structure_match * 0.05  # Up to 5% bonus for good structure match
        
        final_score = min(1.0, base_score + version_bonus + structure_bonus)
        return final_score * 100  # Convert to percentage
    
    def compare_pdf(self, pdf_path):
        """Compare a PDF against the template"""
        print(f"Comparing {pdf_path} against template...")
        
        try:
            # Extract data from test PDF
            test_data = self.extract_pdf_data(pdf_path)
            
            # Check for extraction errors
            if 'error' in test_data:
                raise Exception(f"PDF extraction error: {test_data['error']}")
            
            # Get template lines (normalized)
            template_lines = self.template_data.get('all_lines', [])
            test_lines = test_data.get('all_lines', [])
            
            # Extract version information
            test_version = self.extract_version_info(test_lines)
            template_version = self.extract_version_info(template_lines)
            
            # Calculate text similarity
            similarity_scores = self.calculate_text_similarity(template_lines, test_lines)
            
            # Analyze version match
            version_match = {
                'has_version': test_version['document_id'] is not None,
                'is_t00221': test_version['document_id'] == 'T00221',
                'is_latest': test_version['is_latest'],
                'version_date': test_version['version_date'],
                'template_version_date': template_version['version_date']
            }
            
            # Calculate structure match
            template_structure = self.extract_structure_patterns([self.normalize_german_text(line) for line in template_lines])
            test_structure = self.extract_structure_patterns([self.normalize_german_text(line) for line in test_lines])
            structure_overlap = len(template_structure & test_structure) / len(template_structure | test_structure) if template_structure | test_structure else 0.0
            
            # Calculate overall score
            overall_score = self.calculate_overall_score(similarity_scores, version_match, structure_overlap)
            
            # Determine confidence level
            if overall_score >= 90:
                confidence = "very_high"
                is_template_match = True
            elif overall_score >= 75:
                confidence = "high" 
                is_template_match = True
            elif overall_score >= 60:
                confidence = "medium"
                is_template_match = True
            elif overall_score >= 40:
                confidence = "low"
                is_template_match = False
            else:
                confidence = "very_low"
                is_template_match = False
            
            # Compile results
            result = {
                'file': pdf_path,
                'template_file': self.template_file,
                'comparison_timestamp': datetime.now().isoformat(),
                'overall_score': round(overall_score, 2),
                'is_template_match': is_template_match,
                'confidence': confidence,
                'version_analysis': {
                    'test_version': test_version,
                    'template_version': template_version,
                    'version_match': version_match,
                    'is_latest': test_version['is_latest'],
                    'version_date': test_version['version_date']
                },
                'similarity_breakdown': {
                    metric: round(score * 100, 2) for metric, score in similarity_scores.items()
                },
                'structure_analysis': {
                    'structure_similarity': round(structure_overlap * 100, 2),
                    'template_patterns': len(template_structure),
                    'test_patterns': len(test_structure),
                    'common_patterns': len(template_structure & test_structure)
                },
                'statistics': {
                    'template_lines': len(template_lines),
                    'test_lines': len(test_lines),
                    'template_pages': self.template_data.get('total_pages', 0),
                    'test_pages': test_data.get('total_pages', 0)
                }
            }
            
            return result
            
        except Exception as e:
            return {
                'file': pdf_path,
                'error': str(e),
                'overall_score': 0,
                'is_template_match': False,
                'confidence': 'error'
            }

def main():
    if len(sys.argv) < 2:
        print("Usage: python comparer.py <pdf_file> [template_file] [output_file]")
        print("\nThis script compares a PDF against the T00221 template.")
        print("Default template file: extracted_text.json")
        print("\nExamples:")
        print("  python comparer.py test_document.pdf")
        print("  python comparer.py test_document.pdf my_template.json")
        print("  python comparer.py test_document.pdf extracted_text.json results.json")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    template_file = sys.argv[2] if len(sys.argv) > 2 else "extracted_text.json"
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(pdf_file):
        print(f"Error: PDF file '{pdf_file}' not found.")
        sys.exit(1)
    
    try:
        comparer = PDFTemplateComparer(template_file)
        result = comparer.compare_pdf(pdf_file)
        
        # Generate output filename if not provided
        if output_file is None:
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            output_file = f"{base_name}_comparison.json"
        
        # Save detailed results to file
        try:
            with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Comparison completed successfully!")
            print(f"Detailed results saved to: {output_file}")
            
            # Print clean summary to console
            print(f"\n=== TEMPLATE COMPARISON SUMMARY ===")
            print(f"File: {pdf_file}")
            print(f"Template: {template_file}")
            
            if 'error' in result:
                print(f"❌ ERROR: {result['error']}")
            else:
                score = result.get('overall_score', 0)
                is_match = result.get('is_template_match', False)
                confidence = result.get('confidence', 'unknown')
                
                # Overall assessment
                if is_match:
                    print(f"✅ TEMPLATE MATCH: {score:.1f}% similarity ({confidence} confidence)")
                else:
                    print(f"❌ NOT A MATCH: {score:.1f}% similarity ({confidence} confidence)")
                
                # Version analysis
                version_analysis = result.get('version_analysis', {})
                test_version = version_analysis.get('test_version', {})
                template_version = version_analysis.get('template_version', {})
                
                if test_version.get('document_id'):
                    print(f"\n📄 DOCUMENT VERSION:")
                    print(f"   Document ID: {test_version['document_id']}")
                    print(f"   Version Date: {test_version['version_date']}")
                    
                    if test_version['is_latest']:
                        print(f"   ✅ LATEST VERSION (matches template)")
                    elif template_version.get('version_date'):
                        template_date = template_version['version_date']
                        test_date = test_version['version_date']
                        if test_date and test_date < template_date:
                            print(f"   ⚠️  OLDER VERSION (template: {template_date})")
                        elif test_date and test_date > template_date:
                            print(f"   🆕 NEWER VERSION (template: {template_date})")
                        else:
                            print(f"   📅 DIFFERENT VERSION (template: {template_date})")
                    else:
                        print(f"   ❓ VERSION STATUS UNKNOWN")
                else:
                    print(f"\n❌ NO VERSION INFORMATION FOUND")
                
                # Quick stats
                stats = result.get('statistics', {})
                print(f"\n📊 STATISTICS:")
                print(f"   Test pages: {stats.get('test_pages', 'unknown')}")
                print(f"   Test lines: {stats.get('test_lines', 'unknown')}")
                print(f"   Template pages: {stats.get('template_pages', 'unknown')}")
                print(f"   Template lines: {stats.get('template_lines', 'unknown')}")
                
                # Similarity breakdown (only if detailed)
                similarity = result.get('similarity_breakdown', {})
                if similarity:
                    print(f"\n🔍 SIMILARITY DETAILS:")
                    for metric, score in similarity.items():
                        print(f"   {metric.replace('_', ' ').title()}: {score:.1f}%")
            
            print(f"\n💾 Full details available in: {output_file}")
            
        except Exception as e:
            print(f"Error saving to file {output_file}: {e}")
            print("Falling back to console output:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        error_result = {
            'file': pdf_file,
            'error': str(e),
            'overall_score': 0,
            'is_template_match': False
        }
        
        # Try to save error to file if output_file was specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(error_result, f, indent=2, ensure_ascii=False)
                print(f"Error details saved to: {output_file}")
            except:
                pass
        
        print(f"❌ COMPARISON FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
