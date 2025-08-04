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
import re
from ..decorators import restrict_read_only_users
from ..services.outlook_service import OutlookService
import os

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
            
            # For non-AJAX requests, render the full inbox page with email view 
            # The JavaScript will detect the email_id in the URL and show the email
            pass  # Continue to render the normal inbox page
        
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
    Passes through to main inbox view with email_id parameter for SPA handling.
    """
    try:
        outlook_service = OutlookService()
        email = outlook_service.get_email_by_id(message_id)
        
        if not email:
            raise Http404(_("Email not found"))
        
        # Set email_id in GET parameters and call main inbox view
        request.GET = request.GET.copy()
        request.GET['email_id'] = message_id
        
        # Call the main inbox view which will handle both AJAX and non-AJAX appropriately
        return inbox(request)
        
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
    For non-AJAX requests, redirects to main inbox with compose parameters for SPA handling.
    """
    try:
        # Get compose mode and email ID for reply/forward
        compose_mode = request.GET.get('mode', 'new')
        email_id = request.GET.get('email_id')
        contact_message_id = request.GET.get('contact_message_id')
        
        # Get original email for reply/forward
        original_email = None
        contact_message = None
        
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
        
        # Get contact message for reply to contact message
        if contact_message_id:
            from normieapp.models import ContactMessage
            try:
                contact_message = ContactMessage.objects.get(id=contact_message_id)
                
                # Mark contact message as in progress when composing a reply
                if contact_message.status == 'new':
                    contact_message.status = 'in_progress'
                    if not contact_message.assigned_to:
                        contact_message.assigned_to = request.user
                    contact_message.save()
                    
            except ContactMessage.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Contact message not found'
                    })
                messages.error(request, _('Contact message not found'))
                return redirect('inbox')
        
        context = {
            'page_title': _('Compose Email'),
            'compose_mode': compose_mode,
            'reply_email': original_email if compose_mode == 'reply' else None,
            'forward_email': original_email if compose_mode == 'forward' else None,
            'contact_message': contact_message
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
        
        # For non-AJAX requests, redirect to main inbox with compose parameters
        # This lets the SPA JavaScript handle showing the compose interface
        redirect_url = '/inbox/'
        params = []
        if compose_mode != 'new':
            params.append(f'compose_mode={compose_mode}')
        if email_id:
            params.append(f'compose_email_id={email_id}')
        
        if params:
            redirect_url += '?' + '&'.join(params)
        
        return redirect(redirect_url)
        
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
    Redirects to main inbox compose with mode and email_id parameters for SPA handling.
    """
    try:
        outlook_service = OutlookService()
        original_email = outlook_service.get_email_by_id(message_id)
        
        if not original_email:
            raise Http404(_("Original email not found"))
        
        # Set compose parameters and call main compose view
        request.GET = request.GET.copy()
        request.GET['mode'] = 'reply'
        request.GET['email_id'] = message_id
        
        # Call the main compose view which will handle both AJAX and non-AJAX appropriately
        return inbox_compose(request)
        
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
        from_account = request.POST.get('from_account', '').strip()
        send_on_behalf = request.POST.get('send_on_behalf', '').strip()
        
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
                try:
                    # Create safe filename (remove problematic characters)
                    import re
                    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', file.name)
                    
                    # Save attachment temporarily with normalized path
                    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_attachments')
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    temp_path = os.path.normpath(os.path.join(temp_dir, safe_filename))
                    
                    # Write file with proper error handling
                    with open(temp_path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    
                    # Ensure file is fully written and accessible
                    if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                        attachments.append(temp_path)
                        logger.debug(f"Attachment saved: {temp_path} (size: {os.path.getsize(temp_path)} bytes)")
                    else:
                        logger.error(f"Failed to save attachment: {safe_filename}")
                        
                except Exception as e:
                    logger.error(f"Error processing attachment {file.name}: {str(e)}")
                    continue
        
        # Check if this is a draft save or actual send
        save_as_draft = 'save_draft' in request.POST or request.POST.get('action') == 'save_draft'
        
        # Initialize Outlook service
        outlook_service = OutlookService()
        
        # Determine body format
        body_format = 'html' if body_html and body_html.strip() else 'text'
        final_body = body_html if body_format == 'html' else body_text
        
        if save_as_draft:
            # Save as draft
            try:
                success = outlook_service.save_draft(
                    to_recipients=to_list,
                    subject=subject,
                    body=final_body,
                    cc_recipients=cc_list if cc_list else None,
                    bcc_recipients=bcc_list if bcc_list else None,
                    attachments=attachments if attachments else None,
                    body_format=body_format,
                    from_account=from_account if from_account else None,
                    send_on_behalf=send_on_behalf if send_on_behalf else None
                )
                
                if success:
                    message = 'Draft saved successfully'
                    logger.info(f"Draft saved: '{subject[:30]}...' with {len(to_list)} recipients")
                else:
                    raise Exception('Draft save returned False')
                    
            except Exception as save_error:
                # Clean up temporary attachments on failure
                for attachment_path in attachments:
                    try:
                        if os.path.exists(attachment_path):
                            os.remove(attachment_path)
                    except Exception as cleanup_error:
                        logger.warning(f"Could not delete temporary attachment {attachment_path}: {cleanup_error}")
                
                # Provide specific error message
                error_message = 'Failed to save draft. Please check if Outlook is running and try again.'
                if 'Failed to attach' in str(save_error):
                    error_message = f'Failed to save draft: {str(save_error)}'
                elif 'Attachment not found' in str(save_error):
                    error_message = f'Failed to save draft: {str(save_error)}'
                
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
        else:
            # Send the email
            try:
                success = outlook_service.send_email(
                    to_recipients=to_list,
                    subject=subject,
                    body=final_body,
                    cc_recipients=cc_list if cc_list else None,
                    bcc_recipients=bcc_list if bcc_list else None,
                    attachments=attachments if attachments else None,
                    body_format=body_format,
                    from_account=from_account if from_account else None,
                    send_on_behalf=send_on_behalf if send_on_behalf else None
                )
                
                if success:
                    message = 'Email sent successfully'
                    logger.info(f"Email sent: '{subject[:30]}...' to {len(to_list)} recipients")
                else:
                    raise Exception('Email send returned False')
                    
            except Exception as send_error:
                # Clean up temporary attachments on failure
                for attachment_path in attachments:
                    try:
                        if os.path.exists(attachment_path):
                            os.remove(attachment_path)
                    except Exception as cleanup_error:
                        logger.warning(f"Could not delete temporary attachment {attachment_path}: {cleanup_error}")
                
                # Provide specific error message
                error_message = 'Failed to send email. Please check if Outlook is running and try again.'
                if 'Failed to attach' in str(send_error):
                    error_message = f'Failed to send email: {str(send_error)}'
                elif 'Attachment not found' in str(send_error):
                    error_message = f'Failed to send email: {str(send_error)}'
                
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
        
        # Clean up temporary attachments after successful send/save
        for attachment_path in attachments:
            try:
                if os.path.exists(attachment_path):
                    os.remove(attachment_path)
            except Exception as e:
                logger.warning(f"Could not delete temporary attachment {attachment_path}: {e}")
        
        return JsonResponse({
            'success': True,
            'message': message,
            'sent_to': len(to_list),
            'sent_cc': len(cc_list),
            'sent_bcc': len(bcc_list),
            'subject': subject,
            'action': 'draft_saved' if save_as_draft else 'email_sent'
        })
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to send email. Please try again.'
        }) 

@csrf_exempt
@restrict_read_only_users
def inbox_contact_autocomplete(request):
    """
    API endpoint for contact autocomplete in compose interface.
    Returns contact suggestions for recipient fields.
    """
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        # Validate input
        if not query:
            return JsonResponse({
                'success': True,
                'results': [],
                'message': 'No query provided'
            })
        
        if len(query) < 2:
            return JsonResponse({
                'success': True,
                'results': [],
                'message': 'Query too short (minimum 2 characters)'
            })
        
        # Import contact service
        try:
            from ..services.contact_service import get_contact_service
            contact_service = get_contact_service()
            
            if not contact_service.is_available():
                return JsonResponse({
                    'success': False,
                    'error': 'Contact database not available. Please check configuration.',
                    'results': []
                })
            
            # Perform search
            results = contact_service.search_contacts(query, limit)
            
            return JsonResponse({
                'success': True,
                'query': query,
                'results': results,
                'count': len(results)
            })
            
        except ImportError:
            logger.error("Contact service not available - missing contact_service module")
            return JsonResponse({
                'success': False,
                'error': 'Contact service not configured',
                'results': []
            })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid parameters: {str(e)}',
            'results': []
        })
    except Exception as e:
        logger.error(f"Error in contact autocomplete: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'results': []
        })


@restrict_read_only_users
def inbox_contact_stats(request):
    """
    Get contact database statistics for admin/debugging.
    """
    try:
        from ..services.contact_service import get_contact_service
        contact_service = get_contact_service()
        stats = contact_service.get_database_stats()
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except ImportError:
        return JsonResponse({
            'success': False,
            'error': 'Contact service not available'
        })
    except Exception as e:
        logger.error(f"Error getting contact stats: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        })


@restrict_read_only_users
def inbox_get_accounts(request):
    """
    Get list of available Outlook accounts for sending emails.
    """
    try:
        outlook_service = OutlookService()
        accounts = outlook_service.get_available_accounts()
        
        return JsonResponse({
            'success': True,
            'accounts': accounts
        })
        
    except Exception as e:
        logger.error(f"Error getting available accounts: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'accounts': []
        }) 