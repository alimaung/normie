"""
MLC Check views for Maritime Labour Convention substance lookup.
"""

import json
import os
import tempfile
import shutil
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

# Path to the MLC database file
MLC_DATABASE_PATH = os.path.join(
    settings.BASE_DIR, 
    'normieapp', 'static', 'normieapp', 'data', 'mlc_list.json'
)

# Import SDS detection and CAS extraction modules
try:
    import sys
    import importlib.util
    
    # Add the normstelle path for SDS detector and CAS extractor
    normstelle_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'normstelle', 'ats_workflow', '2 pdfparser')
    if normstelle_path not in sys.path:
        sys.path.append(normstelle_path)
    
    # Import SDS detector
    sds_spec = importlib.util.spec_from_file_location(
        "sds_detector", 
        os.path.join(normstelle_path, 'sds', 'sds_detector.py')
    )
    sds_detector_module = importlib.util.module_from_spec(sds_spec)
    sds_spec.loader.exec_module(sds_detector_module)
    SDSDetector = sds_detector_module.SDSDetector
    
    # Import CAS extractor
    cas_spec = importlib.util.spec_from_file_location(
        "cas_extractor", 
        os.path.join(normstelle_path, 'sds', 'cas_extractor.py')
    )
    cas_extractor_module = importlib.util.module_from_spec(cas_spec)
    cas_spec.loader.exec_module(cas_extractor_module)
    ChemicalExtractor = cas_extractor_module.ChemicalExtractor
    
    SDS_TOOLS_AVAILABLE = True
    logger.info("SDS detector and CAS extractor loaded successfully")
    
except Exception as e:
    logger.error(f"Failed to load SDS tools: {e}")
    SDS_TOOLS_AVAILABLE = False
    SDSDetector = None
    ChemicalExtractor = None

def load_mlc_database():
    """Load the MLC database from JSON file."""
    try:
        with open(MLC_DATABASE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"MLC database file not found: {MLC_DATABASE_PATH}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing MLC database JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading MLC database: {e}")
        return []

@login_required
def mlc_check(request):
    """
    Display the MLC Check page.
    """
    context = {
        'page_title': 'MLC Check',
        'page_description': 'Maritime Labour Convention substance lookup tool',
        'sds_tools_available': SDS_TOOLS_AVAILABLE
    }
    return render(request, 'normieapp/mlc_check.html', context)

@login_required
@require_http_methods(["POST"])
def mlc_search(request):
    """
    Search the MLC database for substances.
    
    Expected POST data:
    {
        "query": "search term",
        "search_fields": ["cas", "ec", "substance"]
    }
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        search_fields = data.get('search_fields', ['cas', 'ec', 'substance'])
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': 'Search query is required'
            })
        
        if len(query) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Search query must be at least 2 characters'
            })
        
        # Load database
        database = load_mlc_database()
        if not database:
            return JsonResponse({
                'success': False,
                'error': 'MLC database is not available'
            })
        
        # Perform search
        results = search_substances(database, query, search_fields)
        
        # Limit results to prevent overwhelming the UI
        max_results = 100
        if len(results) > max_results:
            results = results[:max_results]
            logger.warning(f"Search returned {len(results)} results, limited to {max_results}")
        
        return JsonResponse({
            'success': True,
            'results': results,
            'total_count': len(results),
            'limited': len(results) == max_results
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        logger.error(f"Error in MLC search: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred during search'
        })

@login_required
@require_http_methods(["POST"])
def mlc_process_sds(request):
    """
    Process uploaded SDS document to extract chemical identifiers and search MLC database.
    """
    if not SDS_TOOLS_AVAILABLE:
        return JsonResponse({
            'success': False,
            'error': 'SDS processing tools are not available on this server'
        })
    
    try:
        # Check if file was uploaded
        if 'sds_file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No file uploaded'
            })
        
        uploaded_file = request.FILES['sds_file']
        
        # Validate file type
        if not uploaded_file.name.lower().endswith('.pdf'):
            return JsonResponse({
                'success': False,
                'error': 'Only PDF files are supported'
            })
        
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            return JsonResponse({
                'success': False,
                'error': 'File size must be less than 10MB'
            })
        
        # Save uploaded file temporarily
        temp_file_path = None
        try:
            # Create temporary file
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_file_path, 'wb') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
            
            # Process the SDS document
            result = process_sds_document(
                temp_file_path,
                auto_search=request.POST.get('auto_search') == 'on',
                include_substances=request.POST.get('include_substances') == 'on'
            )
            
            return JsonResponse({
                'success': True,
                **result
            })
            
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    shutil.rmtree(os.path.dirname(temp_file_path))
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file: {e}")
    
    except Exception as e:
        logger.error(f"Error processing SDS document: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing the document'
        })

def process_sds_document(file_path, auto_search=True, include_substances=True):
    """
    Process SDS document using SDS detector and CAS extractor.
    
    Args:
        file_path (str): Path to the PDF file
        auto_search (bool): Whether to automatically search extracted identifiers
        include_substances (bool): Whether to include substance names in search
    
    Returns:
        dict: Processing results
    """
    result = {
        'sds_detection': None,
        'extraction_result': None,
        'search_results': [],
        'processing_notes': []
    }
    
    try:
        # Step 1: SDS Detection
        logger.info(f"Starting SDS detection for: {file_path}")
        sds_detector = SDSDetector()
        sds_score = sds_detector.detect_sds(file_path)
        
        result['sds_detection'] = {
            'total_score': sds_score.total_score,
            'is_likely_sds': sds_score.is_likely_sds,
            'confidence_level': sds_score.confidence_level,
            'breakdown': sds_score.breakdown,
            'detected_features': sds_score.detected_features[:10],  # Limit for JSON response
            'language_detected': sds_score.language_detected
        }
        
        result['processing_notes'].append(f"SDS Detection: {sds_score.confidence_level} confidence ({sds_score.total_score}/100)")
        
        # If it's not likely an SDS, we can still proceed but with a warning
        if not sds_score.is_likely_sds:
            result['processing_notes'].append("Warning: Document may not be a valid SDS")
        
        # Step 2: Chemical Identifier Extraction
        logger.info("Starting chemical identifier extraction")
        extractor = ChemicalExtractor()
        extraction_result = extractor.extract_chemical_identifiers(file_path)
        
        # Convert extraction result to JSON-serializable format
        result['extraction_result'] = {
            'filename': extraction_result.filename,
            'cas_numbers': [
                {
                    'number': id.number,
                    'substance_name': id.substance_name,
                    'concentration': id.concentration,
                    'confidence': id.confidence,
                    'context_phrase': id.context_phrase
                }
                for id in extraction_result.cas_numbers
            ],
            'ec_numbers': [
                {
                    'number': id.number,
                    'substance_name': id.substance_name,
                    'concentration': id.concentration,
                    'confidence': id.confidence,
                    'context_phrase': id.context_phrase
                }
                for id in extraction_result.ec_numbers
            ],
            'reach_numbers': [
                {
                    'number': id.number,
                    'substance_name': id.substance_name,
                    'confidence': id.confidence,
                    'context_phrase': id.context_phrase
                }
                for id in extraction_result.reach_numbers
            ],
            'unique_cas_count': extraction_result.unique_cas_count,
            'unique_ec_count': extraction_result.unique_ec_count,
            'unique_reach_count': extraction_result.unique_reach_count,
            'section_3_found': extraction_result.section_3_found,
            'extraction_confidence': extraction_result.extraction_confidence,
            'extraction_notes': extraction_result.extraction_notes,
            'detected_substances': extraction_result.detected_substances
        }
        
        result['processing_notes'].append(
            f"Extraction: Found {extraction_result.unique_cas_count} CAS, "
            f"{extraction_result.unique_ec_count} EC, {extraction_result.unique_reach_count} REACH numbers"
        )
        
        # Step 3: Automatic MLC Search (if requested)
        if auto_search:
            logger.info("Starting automatic MLC search")
            search_results = []
            database = load_mlc_database()
            
            if database:
                # Search for CAS numbers
                for cas_id in extraction_result.cas_numbers:
                    cas_results = search_substances(database, cas_id.number, ['cas'])
                    search_results.extend(cas_results)
                
                # Search for EC numbers
                for ec_id in extraction_result.ec_numbers:
                    ec_results = search_substances(database, ec_id.number, ['ec'])
                    search_results.extend(ec_results)
                
                # Search for substance names (if requested)
                if include_substances:
                    for substance in extraction_result.detected_substances:
                        if len(substance) > 3:  # Only search meaningful substance names
                            substance_results = search_substances(database, substance, ['substance'])
                            search_results.extend(substance_results)
                
                # Remove duplicates based on CAS number or substance name
                seen = set()
                unique_results = []
                for result_item in search_results:
                    key = result_item.get('CAS_No') or result_item.get('Substance_Name', '')
                    if key and key not in seen:
                        seen.add(key)
                        unique_results.append(result_item)
                
                result['search_results'] = unique_results
                result['processing_notes'].append(f"MLC Search: Found {len(unique_results)} unique matches")
            else:
                result['processing_notes'].append("Warning: MLC database not available for search")
        
        logger.info(f"SDS processing completed successfully: {len(result['search_results'])} MLC matches")
        
    except Exception as e:
        logger.error(f"Error in SDS processing: {e}")
        result['processing_notes'].append(f"Error: {str(e)}")
        raise
    
    return result

def search_substances(database, query, search_fields):
    """
    Search substances in the database based on query and selected fields.
    
    Args:
        database (list): List of substance dictionaries
        query (str): Search query
        search_fields (list): List of fields to search in ['cas', 'ec', 'substance']
    
    Returns:
        list: List of matching substances
    """
    results = []
    query_lower = query.lower()
    
    # Field mapping
    field_mapping = {
        'cas': 'CAS_No',
        'ec': 'EC_No',
        'substance': 'Substance_Name'
    }
    
    for substance in database:
        match_found = False
        
        for field in search_fields:
            if field not in field_mapping:
                continue
                
            db_field = field_mapping[field]
            field_value = substance.get(db_field)
            
            if field_value and isinstance(field_value, str):
                # Exact match for CAS and EC numbers
                if field in ['cas', 'ec']:
                    if query_lower == field_value.lower():
                        match_found = True
                        break
                    # Also check partial match for CAS/EC
                    elif query_lower in field_value.lower():
                        match_found = True
                        break
                
                # Partial match for substance names
                elif field == 'substance':
                    if query_lower in field_value.lower():
                        match_found = True
                        break
        
        if match_found:
            results.append(substance)
    
    # Sort results: exact matches first, then partial matches
    def sort_key(substance):
        exact_match_score = 0
        partial_match_score = 0
        
        for field in search_fields:
            if field not in field_mapping:
                continue
                
            db_field = field_mapping[field]
            field_value = substance.get(db_field)
            
            if field_value and isinstance(field_value, str):
                if query_lower == field_value.lower():
                    exact_match_score += 10
                elif query_lower in field_value.lower():
                    partial_match_score += 1
        
        return (-exact_match_score, -partial_match_score, substance.get('Substance_Name', '').lower())
    
    results.sort(key=sort_key)
    return results

@login_required
def mlc_database_info(request):
    """
    Get information about the MLC database (number of entries, etc.).
    """
    try:
        database = load_mlc_database()
        
        # Calculate some statistics
        total_entries = len(database)
        entries_with_cas = sum(1 for item in database if item.get('CAS_No'))
        entries_with_ec = sum(1 for item in database if item.get('EC_No'))
        
        # Count status types
        status_counts = {}
        for item in database:
            status = item.get('MLC132_Status_by_ROW', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return JsonResponse({
            'success': True,
            'info': {
                'total_entries': total_entries,
                'entries_with_cas': entries_with_cas,
                'entries_with_ec': entries_with_ec,
                'status_counts': status_counts,
                'database_available': True,
                'sds_tools_available': SDS_TOOLS_AVAILABLE
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting MLC database info: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Could not load database information',
            'info': {
                'database_available': False,
                'sds_tools_available': SDS_TOOLS_AVAILABLE
            }
        }) 