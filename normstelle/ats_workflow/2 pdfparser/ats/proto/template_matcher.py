import json
import sys
import os
from difflib import SequenceMatcher
from collections import defaultdict
import re

class PDFTemplateMatcher:
    def __init__(self):
        self.similarity_threshold = 0.7  # Adjustable threshold for template matching
        
    def load_extraction(self, file_path):
        """Load PDF extraction data from JSON file or run extractor"""
        if file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Run extractor on PDF file
            import subprocess
            try:
                result = subprocess.run([
                    sys.executable, 'extractor.py', file_path
                ], capture_output=True, text=True, encoding='utf-8')
                if result.returncode == 0:
                    return json.loads(result.stdout)
                else:
                    raise Exception(f"Extractor failed: {result.stderr}")
            except Exception as e:
                raise Exception(f"Failed to extract from {file_path}: {e}")
    
    def compare_metadata(self, meta1, meta2):
        """Compare PDF metadata for template indicators"""
        score = 0.0
        total_checks = 0
        
        # Compare creator/producer (often indicates same template software)
        for source in ['fitz', 'pypdf']:
            if source in meta1 and source in meta2:
                for field in ['creator', 'producer', 'author']:
                    if field in meta1[source] and field in meta2[source]:
                        total_checks += 1
                        val1 = meta1[source][field].lower().strip()
                        val2 = meta2[source][field].lower().strip()
                        if val1 and val2 and val1 == val2:
                            score += 1.0
                        elif val1 and val2:
                            # Partial match for similar creators/producers
                            similarity = SequenceMatcher(None, val1, val2).ratio()
                            if similarity > 0.8:
                                score += 0.5
        
        return score / max(total_checks, 1), total_checks
    
    def compare_structure(self, struct1, struct2):
        """Compare document structure"""
        score = 0.0
        total_checks = 4
        
        # Page count should match exactly for same template
        if struct1['page_count'] == struct2['page_count']:
            score += 1.0
        
        # Page sizes should be very similar
        if len(struct1['page_sizes']) == len(struct2['page_sizes']):
            page_matches = 0
            for p1, p2 in zip(struct1['page_sizes'], struct2['page_sizes']):
                if (abs(p1['width'] - p2['width']) < 5 and 
                    abs(p1['height'] - p2['height']) < 5):
                    page_matches += 1
            if struct1['page_count'] > 0:
                score += page_matches / struct1['page_count']
        
        # Text block count should be similar (allows for some variance due to content)
        if struct1['total_text_blocks'] > 0 and struct2['total_text_blocks'] > 0:
            ratio = min(struct1['total_text_blocks'], struct2['total_text_blocks']) / max(struct1['total_text_blocks'], struct2['total_text_blocks'])
            if ratio > 0.8:
                score += 1.0
            elif ratio > 0.6:
                score += 0.5
        
        # Drawing count should match closely (template layouts)
        if struct1['total_drawings'] == struct2['total_drawings']:
            score += 1.0
        elif abs(struct1['total_drawings'] - struct2['total_drawings']) <= 2:
            score += 0.5
        
        return score / total_checks, total_checks
    
    def compare_form_fields(self, fields1, fields2):
        """Compare form fields - this is often the strongest indicator"""
        score = 0.0
        total_checks = 3
        
        # Field count should be exactly the same for same template
        if fields1['field_count'] == fields2['field_count']:
            score += 1.0
        elif abs(fields1['field_count'] - fields2['field_count']) <= 2:
            score += 0.5
        
        # Field types should match
        types1 = fields1['field_types']
        types2 = fields2['field_types']
        type_matches = 0
        total_types = len(set(types1.keys()) | set(types2.keys()))
        
        for field_type in set(types1.keys()) | set(types2.keys()):
            count1 = types1.get(field_type, 0)
            count2 = types2.get(field_type, 0)
            if count1 == count2:
                type_matches += 1
            elif abs(count1 - count2) <= 1:
                type_matches += 0.5
        
        if total_types > 0:
            score += type_matches / total_types
        
        # Field names should have high overlap (ignoring values)
        names1 = set(field['name'] for field in fields1['fields'])
        names2 = set(field['name'] for field in fields2['fields'])
        
        if names1 and names2:
            overlap = len(names1 & names2)
            union = len(names1 | names2)
            name_similarity = overlap / union if union > 0 else 0
            score += name_similarity
        
        return score / total_checks, total_checks
    
    def compare_text_patterns(self, text1, text2):
        """Compare text patterns and font usage"""
        score = 0.0
        total_checks = 2
        
        # Compare common text patterns (labels, headers, etc.)
        patterns1 = set(text1['text_patterns'].keys())
        patterns2 = set(text2['text_patterns'].keys())
        
        if patterns1 and patterns2:
            # Look for common static text that appears in templates
            static_patterns1 = {p for p in patterns1 if not re.search(r'\d{2,}|[A-Z]{2,}\d+', p)}
            static_patterns2 = {p for p in patterns2 if not re.search(r'\d{2,}|[A-Z]{2,}\d+', p)}
            
            if static_patterns1 and static_patterns2:
                overlap = len(static_patterns1 & static_patterns2)
                union = len(static_patterns1 | static_patterns2)
                pattern_similarity = overlap / union if union > 0 else 0
                score += pattern_similarity
        
        # Compare font usage patterns
        fonts1 = set(text1['font_usage'].keys())
        fonts2 = set(text2['font_usage'].keys())
        
        if fonts1 and fonts2:
            font_overlap = len(fonts1 & fonts2)
            font_union = len(fonts1 | fonts2)
            font_similarity = font_overlap / font_union if font_union > 0 else 0
            score += font_similarity
        
        return score / total_checks, total_checks
    
    def compare_template_signatures(self, sig1, sig2):
        """Compare the generated template signatures"""
        # Direct hash comparison
        if sig1['signature_hash'] == sig2['signature_hash']:
            return 1.0, 1
        
        # Compare signature elements
        elements1 = set(sig1['signature_elements'])
        elements2 = set(sig2['signature_elements'])
        
        if elements1 and elements2:
            overlap = len(elements1 & elements2)
            union = len(elements1 | elements2)
            return overlap / union if union > 0 else 0, 1
        
        return 0.0, 1
    
    def compare_pdfs(self, pdf1_data, pdf2_data):
        """Compare two PDF extractions and determine template similarity"""
        comparisons = {}
        weights = {
            'metadata': 0.1,
            'structure': 0.2,
            'form_fields': 0.4,  # Highest weight - most reliable indicator
            'text_patterns': 0.2,
            'signature': 0.1
        }
        
        # Perform all comparisons
        comparisons['metadata'] = self.compare_metadata(
            pdf1_data.get('metadata', {}), 
            pdf2_data.get('metadata', {})
        )
        
        comparisons['structure'] = self.compare_structure(
            pdf1_data.get('structure', {}), 
            pdf2_data.get('structure', {})
        )
        
        comparisons['form_fields'] = self.compare_form_fields(
            pdf1_data.get('form_fields', {}), 
            pdf2_data.get('form_fields', {})
        )
        
        comparisons['text_patterns'] = self.compare_text_patterns(
            pdf1_data.get('text', {}), 
            pdf2_data.get('text', {})
        )
        
        comparisons['signature'] = self.compare_template_signatures(
            pdf1_data.get('template_signature', {}), 
            pdf2_data.get('template_signature', {})
        )
        
        # Calculate weighted average
        total_score = 0.0
        total_weight = 0.0
        
        detailed_scores = {}
        for category, (score, checks) in comparisons.items():
            if checks > 0:  # Only include categories with actual data
                detailed_scores[category] = {
                    'score': score,
                    'checks': checks,
                    'weight': weights[category]
                }
                total_score += score * weights[category]
                total_weight += weights[category]
        
        final_score = total_score / total_weight if total_weight > 0 else 0.0
        
        # Determine if it's likely the same template
        is_same_template = final_score >= self.similarity_threshold
        
        return {
            'overall_score': final_score,
            'is_same_template': is_same_template,
            'confidence': 'high' if final_score > 0.85 or final_score < 0.3 else 'medium',
            'detailed_scores': detailed_scores,
            'threshold': self.similarity_threshold
        }
    
    def analyze_template_indicators(self, pdf_data):
        """Analyze what makes this PDF identifiable as a template"""
        indicators = {
            'strong_indicators': [],
            'weak_indicators': [],
            'unique_elements': []
        }
        
        # Form fields are strong indicators
        if pdf_data.get('form_fields', {}).get('field_count', 0) > 0:
            indicators['strong_indicators'].append(
                f"Has {pdf_data['form_fields']['field_count']} form fields"
            )
            
            field_names = [f['name'] for f in pdf_data['form_fields']['fields']]
            if len(field_names) > 5:
                indicators['unique_elements'].extend(field_names[:5])
        
        # Metadata indicators
        metadata = pdf_data.get('metadata', {})
        for source in ['fitz', 'pypdf']:
            if source in metadata:
                creator = metadata[source].get('creator', '').strip()
                producer = metadata[source].get('producer', '').strip()
                if creator:
                    indicators['weak_indicators'].append(f"Creator: {creator}")
                if producer:
                    indicators['weak_indicators'].append(f"Producer: {producer}")
        
        # Text pattern indicators
        text_patterns = pdf_data.get('text', {}).get('text_patterns', {})
        static_patterns = []
        for pattern, count in text_patterns.items():
            if (len(pattern) > 10 and 
                not re.search(r'\d{3,}|[A-Z]{3,}\d+', pattern) and
                len(pattern.split()) > 1):
                static_patterns.append(pattern)
        
        if static_patterns:
            indicators['strong_indicators'].append(
                f"Contains {len(static_patterns)} static text patterns"
            )
            indicators['unique_elements'].extend(static_patterns[:3])
        
        # Structure indicators
        structure = pdf_data.get('structure', {})
        if structure.get('total_drawings', 0) > 10:
            indicators['weak_indicators'].append(
                f"Has {structure['total_drawings']} drawing elements (form layout)"
            )
        
        return indicators

def main():
    if len(sys.argv) < 3:
        print("Usage: python template_matcher.py file1.pdf file2.pdf")
        print("   or: python template_matcher.py file1.json file2.json")
        print("   or: python template_matcher.py analyze file.pdf")
        print("\nThis script compares two PDFs to determine if they come from the same template.")
        print("It can work with PDF files directly or with JSON extraction files.")
        sys.exit(1)
    
    matcher = PDFTemplateMatcher()
    
    if sys.argv[1] == 'analyze' and len(sys.argv) == 3:
        # Analyze single PDF for template indicators
        try:
            pdf_data = matcher.load_extraction(sys.argv[2])
            indicators = matcher.analyze_template_indicators(pdf_data)
            
            result = {
                'file': sys.argv[2],
                'template_indicators': indicators,
                'signature_hash': pdf_data.get('template_signature', {}).get('signature_hash', 'unknown')
            }
            
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"Error analyzing PDF: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        # Compare two PDFs
        try:
            pdf1_data = matcher.load_extraction(sys.argv[1])
            pdf2_data = matcher.load_extraction(sys.argv[2])
            
            comparison = matcher.compare_pdfs(pdf1_data, pdf2_data)
            
            result = {
                'file1': sys.argv[1],
                'file2': sys.argv[2],
                'comparison': comparison
            }
            
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"Error comparing PDFs: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main() 