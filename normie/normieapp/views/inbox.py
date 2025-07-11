from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.conf import settings
from django.core.paginator import Paginator
import os
import json
import logging
from ..decorators import restrict_read_only_users
from ..services.outlook_service import OutlookService

# Configure logger
logger = logging.getLogger(__name__)


@restrict_read_only_users
def inbox(request):
    """
    Main inbox view with Gmail-style interface.
    Displays emails from VBA JSON data with search, filtering, and pagination.
    """
    try:
        # Initialize Outlook service
        outlook_service = OutlookService()
        
        # Get query parameters
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 25))
        search = request.GET.get('search', '').strip()
        filter_unread = request.GET.get('unread') == '1'
        filter_important = request.GET.get('important') == '1'
        filter_attachments = request.GET.get('attachments') == '1'
        sort_by = request.GET.get('sort_by', 'received_time')
        sort_order = request.GET.get('sort_order', 'desc')
        
        # Get emails data
        emails, pagination_info = outlook_service.get_emails_list(
            page=page,
            per_page=per_page,
            search=search if search else None,
            filter_unread=filter_unread if filter_unread else None,
            filter_important=filter_important if filter_important else None,
            filter_attachments=filter_attachments if filter_attachments else None,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Get folder statistics
        folder_stats = outlook_service.get_folder_stats()
        
        # Get data status
        data_status = outlook_service.get_data_status()
        
        # Prepare context
        context = {
            'page_title': _('Email Inbox'),
            'emails': emails,
            'pagination': pagination_info,
            'folder_stats': folder_stats,
            'data_status': data_status,
            'current_filters': {
                'search': search,
                'unread': filter_unread,
                'important': filter_important,
                'attachments': filter_attachments,
                'sort_by': sort_by,
                'sort_order': sort_order
            },
            'per_page_options': [10, 25, 50, 100]
        }
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'emails': emails,
                'pagination': pagination_info,
                'folder_stats': folder_stats
            })
        
        return render(request, 'normieapp/inbox.html', context)
        
    except Exception as e:
        logger.error(f"Error in inbox view: {str(e)}")
        messages.error(request, _('Error loading inbox. Please try again.'))
        
        context = {
            'page_title': _('Email Inbox'),
            'emails': [],
            'pagination': {'current_page': 1, 'total_pages': 0, 'total_count': 0},
            'folder_stats': {'total_emails': 0, 'unread_emails': 0},
            'data_status': {'available': False, 'message': 'Error loading data'},
            'current_filters': {},
            'per_page_options': [10, 25, 50, 100]
        }
        
        return render(request, 'normieapp/inbox.html', context)


@restrict_read_only_users
def inbox_view_message(request, message_id):
    """
    View a specific email message.
    """
    try:
        outlook_service = OutlookService()
        email = outlook_service.get_email_by_id(message_id)
        
        if not email:
            raise Http404(_("Email not found"))
        
        context = {
            'page_title': _('View Email'),
            'email': email,
            'message_id': message_id
        }
        
        return render(request, 'normieapp/inbox_view.html', context)
        
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error viewing email {message_id}: {str(e)}")
        messages.error(request, _('Error loading email. Please try again.'))
        return redirect('inbox')


@login_required
@restrict_read_only_users
def inbox_compose(request):
    """
    Compose a new email message.
    """
    context = {
        'page_title': _('Compose Email'),
        'compose_mode': 'new'
    }
    
    return render(request, 'normieapp/inbox_compose.html', context)


@login_required
@restrict_read_only_users
def inbox_reply(request, message_id):
    """
    Reply to an email message.
    """
    try:
        outlook_service = OutlookService()
        original_email = outlook_service.get_email_by_id(message_id)
        
        if not original_email:
            raise Http404(_("Original email not found"))
        
        context = {
            'page_title': _('Reply to Email'),
            'original_email': original_email,
            'message_id': message_id,
            'compose_mode': 'reply'
        }
        
        return render(request, 'normieapp/inbox_compose.html', context)
        
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error replying to email {message_id}: {str(e)}")
        messages.error(request, _('Error loading email for reply. Please try again.'))
        return redirect('inbox')


@csrf_exempt
@restrict_read_only_users
def inbox_search(request):
    """
    AJAX endpoint for email search.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        search_query = data.get('query', '').strip()
        
        outlook_service = OutlookService()
        emails, pagination_info = outlook_service.get_emails_list(
            search=search_query if search_query else None,
            per_page=25
        )
        
        return JsonResponse({
            'success': True,
            'emails': emails,
            'pagination': pagination_info,
            'query': search_query
        })
        
    except Exception as e:
        logger.error(f"Error in inbox search: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Search failed'})


@csrf_exempt
@restrict_read_only_users
def inbox_refresh(request):
    """
    AJAX endpoint to refresh inbox data.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        outlook_service = OutlookService()
        
        # Get current filters from request
        data = json.loads(request.body) if request.body else {}
        page = data.get('page', 1)
        search = data.get('search')
        filter_unread = data.get('unread')
        filter_important = data.get('important')
        filter_attachments = data.get('attachments')
        
        emails, pagination_info = outlook_service.get_emails_list(
            page=page,
            search=search,
            filter_unread=filter_unread,
            filter_important=filter_important,
            filter_attachments=filter_attachments
        )
        
        folder_stats = outlook_service.get_folder_stats()
        data_status = outlook_service.get_data_status()
        
        return JsonResponse({
            'success': True,
            'emails': emails,
            'pagination': pagination_info,
            'folder_stats': folder_stats,
            'data_status': data_status,
            'timestamp': data_status.get('last_modified', 'Unknown')
        })
        
    except Exception as e:
        logger.error(f"Error refreshing inbox: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Refresh failed'})


@csrf_exempt
@restrict_read_only_users
def inbox_get_attachment(request, message_id, filename):
    """
    Download an email attachment.
    """
    try:
        outlook_service = OutlookService()
        attachment_path = outlook_service.get_attachment_path(message_id, filename)
        
        if not attachment_path:
            raise Http404(_("Attachment not found"))
        
        # Read and serve the file
        with open(attachment_path, 'rb') as f:
            response = HttpResponse(f.read())
            
        # Set appropriate headers
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Try to determine content type
        if filename.lower().endswith('.pdf'):
            response['Content-Type'] = 'application/pdf'
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            response['Content-Type'] = 'image/jpeg'
        elif filename.lower().endswith('.png'):
            response['Content-Type'] = 'image/png'
        elif filename.lower().endswith('.doc'):
            response['Content-Type'] = 'application/msword'
        elif filename.lower().endswith('.docx'):
            response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            response['Content-Type'] = 'application/octet-stream'
            
        return response
        
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Error downloading attachment {filename} from {message_id}: {str(e)}")
        raise Http404(_("Attachment not found"))


@csrf_exempt
@restrict_read_only_users
def inbox_delete_message(request, message_id):
    """
    Delete a specific email message (placeholder for future COM implementation).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    return JsonResponse({
        'success': False, 
        'message': 'Email deletion will be implemented with COM integration.'
    })


@csrf_exempt
@restrict_read_only_users
def inbox_delete(request):
    """
    Delete multiple email messages (placeholder for future COM implementation).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    return JsonResponse({
        'success': False, 
        'error': 'Bulk email deletion will be implemented with COM integration.'
    })


@csrf_exempt
@restrict_read_only_users
def inbox_categorize_message(request, message_id):
    """
    Apply a category to a specific email message (placeholder for future COM implementation).
    """
    return JsonResponse({
        'success': False, 
        'message': 'Email categorization will be implemented with COM integration.'
    })


@csrf_exempt
@restrict_read_only_users
def inbox_categorize(request):
    """
    Apply a category to multiple email messages (placeholder for future COM implementation).
    """
    return JsonResponse({
        'success': False, 
        'error': 'Bulk email categorization will be implemented with COM integration.'
    })


@csrf_exempt
@restrict_read_only_users
def inbox_mark_read(request):
    """
    Mark emails as read/unread (placeholder for future COM implementation).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    return JsonResponse({
        'success': False, 
        'error': 'Mark as read/unread will be implemented with COM integration.'
    })


@restrict_read_only_users
def inbox_status(request):
    """
    Get inbox status information.
    """
    try:
        outlook_service = OutlookService()
        data_status = outlook_service.get_data_status()
        folder_stats = outlook_service.get_folder_stats()
        
        return JsonResponse({
            'success': True,
            'data_status': data_status,
            'folder_stats': folder_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting inbox status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to get inbox status'
        }) 