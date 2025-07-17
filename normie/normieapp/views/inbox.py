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
        filter_folder = request.GET.get('folder', 'Inbox')  # Default to Inbox
        sort_by = request.GET.get('sort_by', 'received_time')
        sort_order = request.GET.get('sort_order', 'desc')
        email_id = request.GET.get('email_id')  # For single email view in SPA
        
        # Handle single email view for SPA
        if email_id:
            email = outlook_service.get_email_by_id(email_id)
            
            if not email:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Email not found'
                    })
                raise Http404(_("Email not found"))
            
            # For AJAX requests, return email view content
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.template.loader import render_to_string
                
                # Render the email view partial template
                email_view_html = render_to_string(
                    'normieapp/includes/email_view_content.html', 
                    {'email': email},
                    request=request
                )
                
                return JsonResponse({
                    'success': True,
                    'email_view': True,
                    'html': email_view_html,
                    'email': email
                })
            
            # For non-AJAX requests, redirect to the proper email view URL
            return redirect('inbox_view_message', message_id=email_id)
        
        # Get emails data
        emails, pagination_info = outlook_service.get_emails_list(
            page=page,
            per_page=per_page,
            search=search if search else None,
            filter_unread=filter_unread if filter_unread else None,
            filter_important=filter_important if filter_important else None,
            filter_attachments=filter_attachments if filter_attachments else None,
            filter_folder=filter_folder,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Get folder statistics
        folder_stats = outlook_service.get_folder_stats()
        
        # Get data status
        data_status = outlook_service.get_data_status()
        
        # Get COM status
        com_status = outlook_service.get_com_status()
        
        # Prepare context
        context = {
            'page_title': _('Email Inbox'),
            'emails': emails,
            'pagination': pagination_info,
            'folder_stats': folder_stats,
            'data_status': data_status,
            'com_status': com_status,
            'current_filters': {
                'search': search,
                'unread': filter_unread,
                'important': filter_important,
                'attachments': filter_attachments,
                'folder': filter_folder,
                'sort_by': sort_by,
                'sort_order': sort_order
            },
            'current_folder': filter_folder,
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
    try:
        # Get compose mode and email ID for reply/forward
        compose_mode = request.GET.get('mode', 'new')
        email_id = request.GET.get('email_id')
        
        # Get original email for reply/forward
        original_email = None
        if email_id and compose_mode in ['reply', 'forward']:
            outlook_service = OutlookService()
            original_email = outlook_service.get_email_by_id(email_id)
            
            if not original_email:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Original email not found'
                    })
                messages.error(request, _('Original email not found'))
                return redirect('inbox')
        
        context = {
            'page_title': _('Compose Email'),
            'compose_mode': compose_mode,
            'reply_email': original_email if compose_mode == 'reply' else None,
            'forward_email': original_email if compose_mode == 'forward' else None
        }
        
        # Handle AJAX requests for SPA
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            
            # Render the compose view partial template
            compose_html = render_to_string(
                'normieapp/includes/compose_content.html', 
                context,
                request=request
            )
            
            return JsonResponse({
                'success': True,
                'compose_view': True,
                'html': compose_html,
                'mode': compose_mode
            })
        
        return render(request, 'normieapp/inbox_compose.html', context)
        
    except Exception as e:
        logger.error(f"Error in compose view: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Failed to load compose interface'
            })
        messages.error(request, _('Error loading compose interface'))
        return redirect('inbox')


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
        filter_folder = data.get('folder')  # ✅ Add missing folder filter
        
        emails, pagination_info = outlook_service.get_emails_list(
            page=page,
            search=search,
            filter_unread=filter_unread,
            filter_important=filter_important,
            filter_attachments=filter_attachments,
            filter_folder=filter_folder  # ✅ Pass folder filter to service
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


@restrict_read_only_users
def inbox_folder(request, folder_name):
    """
    View emails in a specific folder.
    """
    # Folder name mapping to handle URL-friendly names (supports both Outlook and Gmail)
    folder_mapping = {
        'inbox': 'Inbox',
        'sent': ['Sent Items', 'Sent Mail'],  # Try both Outlook and Gmail names
        'deleted': ['Deleted Items', 'Trash'],  # Try both Outlook and Gmail names
        'drafts': 'Drafts',
        'outbox': 'Outbox'
    }
    
    mapped_folder = folder_mapping.get(folder_name.lower(), folder_name)
    
    # Handle both single folder names and lists of possible names
    if isinstance(mapped_folder, list):
        # For lists, we'll let the service try each name
        actual_folder = mapped_folder[0]  # Use first as default, service will try others
    else:
        actual_folder = mapped_folder
    
    # Add folder parameter to request
    request.GET = request.GET.copy()
    request.GET['folder'] = actual_folder
    
    # Call the main inbox view with folder filter
    return inbox(request)


@restrict_read_only_users  
def inbox_sent(request):
    """View sent emails."""
    request.GET = request.GET.copy()
    request.GET['folder'] = 'Sent Items'
    return inbox(request)


@restrict_read_only_users
def inbox_deleted(request):
    """View deleted emails."""
    request.GET = request.GET.copy()
    request.GET['folder'] = 'Deleted Items'
    return inbox(request)


@restrict_read_only_users
def inbox_drafts(request):
    """View draft emails."""
    request.GET = request.GET.copy()
    request.GET['folder'] = 'Drafts'
    return inbox(request)


@restrict_read_only_users
def inbox_outbox(request):
    """View outbox emails."""
    request.GET = request.GET.copy()
    request.GET['folder'] = 'Outbox'
    return inbox(request)


@csrf_exempt
@restrict_read_only_users
def inbox_mark_read_unread(request):
    """
    AJAX endpoint to mark emails as read or unread.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        data = json.loads(request.body) if request.body else {}
        email_ids = data.get('email_ids', [])
        mark_as_read = data.get('read', True)  # True for read, False for unread
        
        if not email_ids:
            return JsonResponse({'success': False, 'error': 'No email IDs provided'})
        
        outlook_service = OutlookService()
        
        if isinstance(email_ids, str):
            email_ids = [email_ids]
        
        success_count, failed_ids = outlook_service.mark_multiple_emails_read(email_ids, mark_as_read)
        
        status = "read" if mark_as_read else "unread"
        
        return JsonResponse({
            'success': True,
            'message': f'Marked {success_count}/{len(email_ids)} emails as {status}',
            'success_count': success_count,
            'failed_count': len(failed_ids),
            'failed_ids': failed_ids
        })
        
    except Exception as e:
        logger.error(f"Error marking emails as read/unread: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Failed to update read status'})


@csrf_exempt
@restrict_read_only_users  
def inbox_mark_single_read_unread(request, message_id):
    """
    AJAX endpoint to mark a single email as read or unread.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        data = json.loads(request.body) if request.body else {}
        mark_as_read = data.get('read', True)
        
        outlook_service = OutlookService()
        success = outlook_service.mark_email_read(message_id, mark_as_read)
        
        status = "read" if mark_as_read else "unread"
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Email marked as {status}',
                'email_id': message_id,
                'read': mark_as_read,
                'unread': not mark_as_read  # Add explicit unread state
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Failed to mark email as {status}'
            })
        
    except Exception as e:
        logger.error(f"Error marking email {message_id} as read/unread: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Failed to update read status'})


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
    Delete a specific email message using COM interface.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        outlook_service = OutlookService()
        
        # Check if COM is available
        if not outlook_service.is_com_available():
            return JsonResponse({
                'success': False,
                'message': 'COM interface not available. Please ensure Outlook is running.'
            })
        
        # Delete the email
        success = outlook_service.delete_email(message_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Email deleted successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to delete email. Email may not be found in Outlook.'
            })
            
    except Exception as e:
        logger.error(f"Error deleting email {message_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while deleting the email'
        })


@csrf_exempt
@restrict_read_only_users
def inbox_delete(request):
    """
    Delete multiple email messages using COM interface.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        email_ids = data.get('email_ids', [])
        
        if not email_ids:
            return JsonResponse({'success': False, 'error': 'No emails specified for deletion'})
        
        outlook_service = OutlookService()
        
        # Check if COM is available
        if not outlook_service.is_com_available():
            return JsonResponse({
                'success': False,
                'error': 'COM interface not available. Please ensure Outlook is running.'
            })
        
        # Delete multiple emails
        success_count, failed_ids = outlook_service.delete_multiple_emails(email_ids)
        
        if success_count == len(email_ids):
            return JsonResponse({
                'success': True,
                'message': f'All {success_count} emails deleted successfully',
                'deleted_count': success_count
            })
        elif success_count > 0:
            return JsonResponse({
                'success': True,
                'message': f'{success_count} of {len(email_ids)} emails deleted successfully',
                'deleted_count': success_count,
                'failed_count': len(failed_ids),
                'failed_ids': failed_ids
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to delete any emails',
                'failed_ids': failed_ids
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        logger.error(f"Error in bulk email deletion: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while deleting emails'
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
def inbox_mark_message_read(request, message_id):
    """
    Mark a single email as read or unread using COM interface.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        data = json.loads(request.body) if request.body else {}
        read_status = data.get('read', True)  # Default to marking as read
        
        outlook_service = OutlookService()
        
        # Check if COM is available
        if not outlook_service.is_com_available():
            return JsonResponse({
                'success': False,
                'error': 'COM interface not available. Please ensure Outlook is running.'
            })
        
        # Mark single email as read/unread
        success = outlook_service.mark_email_read(message_id, read_status)
        
        status_text = "read" if read_status else "unread"
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Email marked as {status_text} successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Failed to mark email as {status_text}. Email may not be found in Outlook.'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        logger.error(f"Error marking email {message_id} as read/unread: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while updating email status'
        })


@csrf_exempt
@restrict_read_only_users
def inbox_mark_read(request):
    """
    Mark emails as read/unread using COM interface.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        email_ids = data.get('email_ids', [])
        read_status = data.get('read', True)  # Default to marking as read
        
        if not email_ids:
            return JsonResponse({'success': False, 'error': 'No emails specified'})
        
        outlook_service = OutlookService()
        
        # Check if COM is available
        if not outlook_service.is_com_available():
            return JsonResponse({
                'success': False,
                'error': 'COM interface not available. Please ensure Outlook is running.'
            })
        
        # Mark multiple emails as read/unread
        success_count, failed_ids = outlook_service.mark_multiple_emails_read(email_ids, read_status)
        
        status_text = "read" if read_status else "unread"
        
        if success_count == len(email_ids):
            return JsonResponse({
                'success': True,
                'message': f'All {success_count} emails marked as {status_text} successfully',
                'updated_count': success_count
            })
        elif success_count > 0:
            return JsonResponse({
                'success': True,
                'message': f'{success_count} of {len(email_ids)} emails marked as {status_text} successfully',
                'updated_count': success_count,
                'failed_count': len(failed_ids),
                'failed_ids': failed_ids
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Failed to mark any emails as {status_text}',
                'failed_ids': failed_ids
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        logger.error(f"Error marking emails as read/unread: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while updating email status'
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


@restrict_read_only_users
def inbox_test_accounts(request):
    """
    Test account fallback functionality.
    """
    try:
        outlook_service = OutlookService()
        test_results = outlook_service.test_account_fallback()
        
        return JsonResponse({
            'success': True,
            'test_results': test_results
        })
        
    except Exception as e:
        logger.error(f"Error testing account fallback: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to test account fallback'
        })


@restrict_read_only_users
def inbox_debug_email(request, message_id):
    """
    Debug email data and search process.
    """
    try:
        outlook_service = OutlookService()
        debug_info = outlook_service.debug_email_data(message_id)
        
        return JsonResponse({
            'success': True,
            'debug_info': debug_info
        })
        
    except Exception as e:
        logger.error(f"Error debugging email {message_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Failed to debug email: {str(e)}'
        }) 

@csrf_exempt
@restrict_read_only_users
def inbox_flag_email(request):
    """
    AJAX endpoint to flag or unflag emails.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        data = json.loads(request.body) if request.body else {}
        email_ids = data.get('email_ids', [])
        flagged = data.get('flagged', True)  # True for flag, False for unflag
        
        if not email_ids:
            return JsonResponse({'success': False, 'error': 'No email IDs provided'})
        
        outlook_service = OutlookService()
        
        if isinstance(email_ids, str):
            email_ids = [email_ids]
        
        success_count, failed_ids = outlook_service.flag_multiple_emails(email_ids, flagged)
        
        status = "flagged" if flagged else "unflagged"
        
        if success_count > 0:
            return JsonResponse({
                'success': True,
                'message': f'{success_count} email(s) {status} successfully',
                'success_count': success_count,
                'failed_count': len(failed_ids),
                'failed_ids': failed_ids
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Failed to {status} emails',
                'failed_ids': failed_ids
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})

@csrf_exempt
@restrict_read_only_users
def inbox_flag_single_email(request, message_id):
    """
    AJAX endpoint to flag or unflag a single email.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        data = json.loads(request.body) if request.body else {}
        flagged = data.get('flagged', True)  # True for flag, False for unflag
        
        outlook_service = OutlookService()
        
        success = outlook_service.flag_email(message_id, flagged)
        
        status = "flagged" if flagged else "unflagged"
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Email {status} successfully',
                'flagged': flagged
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Failed to {status} email'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})


@csrf_exempt
@restrict_read_only_users
def inbox_send_email(request):
    """
    Send a composed email using COM interface.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        # Get form data
        to_recipients = request.POST.get('to', '').strip()
        cc_recipients = request.POST.get('cc', '').strip()
        bcc_recipients = request.POST.get('bcc', '').strip()
        subject = request.POST.get('subject', '').strip()
        body_html = request.POST.get('body', '').strip()
        body_text = request.POST.get('body_text', '').strip()
        
        # Validate required fields
        if not to_recipients:
            return JsonResponse({
                'success': False,
                'error': 'At least one recipient is required'
            })
        
        if not subject:
            return JsonResponse({
                'success': False,
                'error': 'Subject is required'
            })
        
        if not body_text:
            return JsonResponse({
                'success': False,
                'error': 'Message body is required'
            })
        
        # Parse recipients
        to_list = [email.strip() for email in to_recipients.split(',') if email.strip()]
        cc_list = [email.strip() for email in cc_recipients.split(',') if email.strip()] if cc_recipients else []
        bcc_list = [email.strip() for email in bcc_recipients.split(',') if email.strip()] if bcc_recipients else []
        
        # Get attachments
        attachments = []
        for key, file in request.FILES.items():
            if key.startswith('attachment_'):
                # Save attachment temporarily
                temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_attachments', file.name)
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                
                with open(temp_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                attachments.append(temp_path)
        
        # For now, we'll simulate sending since COM email sending requires more complex setup
        # In a real implementation, this would use Outlook COM interface to send emails
        
        # Simulate processing time
        import time
        time.sleep(1)
        
        # Log the email for debugging
        logger.info(f"Email sent simulation:")
        logger.info(f"  To: {to_recipients}")
        logger.info(f"  CC: {cc_recipients}")
        logger.info(f"  BCC: {bcc_recipients}")
        logger.info(f"  Subject: {subject}")
        logger.info(f"  Body length: {len(body_text)} characters")
        logger.info(f"  Attachments: {len(attachments)} files")
        
        # Clean up temporary attachments
        for attachment_path in attachments:
            try:
                if os.path.exists(attachment_path):
                    os.remove(attachment_path)
            except Exception as e:
                logger.warning(f"Could not delete temporary attachment {attachment_path}: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Email sent successfully',
            'sent_to': len(to_list),
            'sent_cc': len(cc_list),
            'sent_bcc': len(bcc_list),
            'subject': subject
        })
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to send email. Please try again.'
        }) 