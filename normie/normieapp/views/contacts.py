"""
Contact Management Views

Provides views for viewing, searching, and managing contacts from the
OAB contact database.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db import transaction
import logging
import json

from ..decorators import restrict_read_only_users
from ..services.contact_service import get_contact_service

logger = logging.getLogger(__name__)


@login_required
@restrict_read_only_users
def contacts_page(request):
    """
    Main contacts management page with search and filtering.
    """
    try:
        contact_service = get_contact_service()
        stats = contact_service.get_database_stats()
        
        context = {
            'page_title': 'Contact Management',
            'contact_stats': stats,
            'is_available': stats.get('available', False)
        }
        
        return render(request, 'normieapp/contacts.html', context)
        
    except Exception as e:
        logger.error(f"Error in contacts page: {str(e)}", exc_info=True)
        context = {
            'page_title': 'Contact Management',
            'contact_stats': {'available': False, 'total_contacts': 0},
            'is_available': False,
            'error': 'Failed to load contacts'
        }
        return render(request, 'normieapp/contacts.html', context)


@csrf_exempt
@restrict_read_only_users
def contacts_search(request):
    """
    AJAX endpoint for contact search with pagination and filtering.
    """
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        # Get search parameters
        query = request.GET.get('q', '').strip()
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 25)), 100)  # Max 100 per page
        sort_by = request.GET.get('sort_by', 'name')
        sort_order = request.GET.get('sort_order', 'asc')
        
        contact_service = get_contact_service()
        
        if not contact_service.is_available():
            return JsonResponse({
                'success': False,
                'error': 'Contact database not available'
            })
        
        # Perform search with larger limit for pagination
        search_limit = per_page * 10  # Get more results for better pagination
        results = contact_service.search_contacts(query, limit=search_limit) if query else []
        
        # Apply sorting
        if sort_by == 'name':
            results.sort(key=lambda x: (x.get('display_name') or x.get('name') or '').lower(), 
                        reverse=(sort_order == 'desc'))
        elif sort_by == 'email':
            results.sort(key=lambda x: (x.get('email') or '').lower(), 
                        reverse=(sort_order == 'desc'))
        elif sort_by == 'company':
            results.sort(key=lambda x: (x.get('company') or '').lower(), 
                        reverse=(sort_order == 'desc'))
        
        # Paginate results
        paginator = Paginator(results, per_page)
        page_obj = paginator.get_page(page)
        
        return JsonResponse({
            'success': True,
            'query': query,
            'results': list(page_obj),
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'per_page': per_page,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'start_index': page_obj.start_index(),
                'end_index': page_obj.end_index()
            }
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid parameters: {str(e)}'
        })
    except Exception as e:
        logger.error(f"Error in contacts search: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Search failed'
        })


@csrf_exempt
@restrict_read_only_users
def contact_detail(request, email):
    """
    Get detailed information for a specific contact by email.
    """
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        contact_service = get_contact_service()
        
        if not contact_service.is_available():
            return JsonResponse({
                'success': False,
                'error': 'Contact database not available'
            })
        
        contact = contact_service.get_contact_by_email(email)
        
        if contact:
            return JsonResponse({
                'success': True,
                'contact': contact
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Contact not found'
            }, status=404)
            
    except Exception as e:
        logger.error(f"Error getting contact detail for {email}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to get contact details'
        })


@csrf_exempt
@restrict_read_only_users
def contacts_export(request):
    """
    Export contacts to CSV format.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        export_format = data.get('format', 'csv')
        query = data.get('query', '').strip()
        
        contact_service = get_contact_service()
        
        if not contact_service.is_available():
            return JsonResponse({
                'success': False,
                'error': 'Contact database not available'
            })
        
        # Get contacts to export
        if query:
            contacts = contact_service.search_contacts(query, limit=10000)
        else:
            # For now, limit exports to prevent performance issues
            return JsonResponse({
                'success': False,
                'error': 'Please provide a search query to limit export size'
            })
        
        if export_format == 'csv':
            # Generate CSV content
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Display Name', 'Email', 'Company', 'Department', 
                'Title', 'Phone', 'Office'
            ])
            
            # Write contact data
            for contact in contacts:
                writer.writerow([
                    contact.get('display_name', ''),
                    contact.get('email', ''),
                    contact.get('company', ''),
                    contact.get('department', ''),
                    contact.get('title', ''),
                    contact.get('phone', ''),
                    contact.get('office', '')
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            return JsonResponse({
                'success': True,
                'filename': f'contacts_export_{query or "all"}.csv',
                'content': csv_content,
                'count': len(contacts)
            })
        
        else:
            return JsonResponse({
                'success': False,
                'error': 'Unsupported export format'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        logger.error(f"Error exporting contacts: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Export failed'
        })


@restrict_read_only_users
def contacts_stats(request):
    """
    Get detailed contact database statistics.
    """
    try:
        contact_service = get_contact_service()
        stats = contact_service.get_database_stats()
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting contact stats: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to get statistics'
        }) 