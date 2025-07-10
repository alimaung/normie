from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.conf import settings
import os
import json
import logging
from ..decorators import restrict_read_only_users

# Configure logger
logger = logging.getLogger(__name__)


@restrict_read_only_users
def inbox(request):
    """
    Email inbox view - requires applicant role or above.
    Displays emails from allowed accounts.
    """
    from ..services.outlook_service import OutlookService
    
    # Default to the first allowed account
    email_address = request.GET.get('account', OutlookService.ALLOWED_ACCOUNTS[0])
    folder_type = request.GET.get('folder', 'inbox')
    search_term = request.GET.get('search')
    category = request.GET.get('category')
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 25))
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    context = {
        'page_title': _('Email Inbox'),
        'email_address': email_address,
        'folder_type': folder_type,
        'search_term': search_term,
        'category': category,
        'page': page,
        'per_page': per_page,
        'allowed_accounts': OutlookService.ALLOWED_ACCOUNTS,
        'emails': [],  # Default empty list
        'has_next': False,
        'has_prev': page > 1
    }
    
    # Default categories if we can't fetch them
    default_categories = [
        {"name": "Important", "color": "#FF0000"},
        {"name": "Work", "color": "#FFA500"},
        {"name": "Personal", "color": "#0000FF"},
        {"name": "Follow-up", "color": "#008000"},
        {"name": "Project", "color": "#800080"}
    ]
    context['available_categories'] = default_categories
    
    try:
        # Connect to Outlook - VBA handles account targeting automatically
        outlook = OutlookService()
        
        # Categories are disabled - using default categories
        context['available_categories'] = default_categories
        
        # Fetch emails
        try:
            emails = outlook.get_emails(
                email_address=email_address,
                folder_type=folder_type,
                limit=per_page,
                offset=offset,
                search_term=search_term,
                category=category
            )
            
            # Add emails to context
            context['emails'] = emails
            
            # Check if we're using VBA data
            if emails and any(email.get('source') == 'vba' for email in emails):
                context['using_vba_data'] = True
                context['vba_data_info'] = True
                messages.info(request, _("📧 Displaying emails from VBA cache (updated every minute). Actions like delete and categorize work in real-time via COM."))
            
            # Add pagination info
            context['has_next'] = len(emails) == per_page
            context['has_prev'] = page > 1
            
            if not emails and page == 1:
                messages.info(request, _("No emails found in this folder."))
                
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            messages.error(request, _(f"Could not fetch emails: {str(e)}"))
            context['error'] = True
        
    except ConnectionError as e:
        messages.error(request, str(e))
        context['connection_error'] = True
    except ValueError as e:
        messages.error(request, str(e))
        context['value_error'] = True
    except Exception as e:
        messages.error(request, _(f"An unexpected error occurred: {str(e)}"))
        context['error'] = True
    
    return render(request, 'normieapp/inbox.html', context)


@restrict_read_only_users
def inbox_view_message(request, message_id):
    """
    View a specific email message.
    """
    from ..services.outlook_service import OutlookService
    
    # Get email address from query params
    email_address = request.GET.get('account', OutlookService.ALLOWED_ACCOUNTS[0])
    
    context = {
        'page_title': _('View Email'),
        'email_address': email_address,
        'allowed_accounts': OutlookService.ALLOWED_ACCOUNTS,
    }
    
    try:
        # Connect to Outlook - VBA handles account targeting automatically
        outlook = OutlookService()
        
        try:
            # Get the email
            email = outlook.get_email(email_address, message_id)
            
            if not email:
                messages.error(request, _('Email not found.'))
                return redirect('inbox')
            
            # Add email to context
            context['email'] = email
            
            # Try to mark as read (skip for VBA emails)
            if not message_id.startswith('vba_'):
                try:
                    outlook.mark_as_read(email_address, message_id)
                except Exception as e:
                    logger.warning(f"Could not mark email as read: {str(e)}")
                    # Not critical, continue without showing error to user
            else:
                logger.debug("Skipping mark as read for VBA email")
        except Exception as e:
            messages.error(request, _(f"Could not retrieve email: {str(e)}"))
            return redirect('inbox')
        
    except ConnectionError as e:
        messages.error(request, str(e))
        return redirect('inbox')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('inbox')
    except Exception as e:
        messages.error(request, _(f"An unexpected error occurred: {str(e)}"))
        return redirect('inbox')
    
    return render(request, 'normieapp/inbox_view.html', context)


@login_required
@restrict_read_only_users
def inbox_compose(request):
    """
    Compose a new email message.
    """
    from ..services.outlook_service import OutlookService
    
    # Get email address from query params
    email_address = request.GET.get('account', OutlookService.ALLOWED_ACCOUNTS[0])
    
    # Create the compose form
    context = {
        'page_title': _('Compose Email'),
        'email_address': email_address,
        'allowed_accounts': OutlookService.ALLOWED_ACCOUNTS,
    }
    
    # VBA handles account targeting automatically
    return render(request, 'normieapp/inbox_compose.html', context)


@csrf_exempt
@restrict_read_only_users
def inbox_delete_message(request, message_id):
    """
    Delete a specific email message.
    """
    from ..services.outlook_service import OutlookService
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    # Check if this is a VBA email ID
    if message_id.startswith('vba_'):
        return JsonResponse({
            'success': False, 
            'message': 'Cannot delete emails from VBA cache. Please wait for the next refresh or use Outlook directly.'
        })
    
    # Get email address from request
    try:
        data = json.loads(request.body)
        email_address = data.get('email_address', OutlookService.ALLOWED_ACCOUNTS[0])
    except:
        email_address = request.POST.get('account', OutlookService.ALLOWED_ACCOUNTS[0])
    
    try:
        # Connect to Outlook and delete the email
        outlook = OutlookService()
        success = outlook.delete_email(email_address, message_id)
        
        if success:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Failed to delete email'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@csrf_exempt
@restrict_read_only_users
def inbox_delete(request):
    """
    Delete multiple email messages.
    """
    from ..services.outlook_service import OutlookService
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    # Get email IDs and account from request
    email_ids = request.POST.getlist('email_ids[]') or json.loads(request.POST.get('email_ids', '[]'))
    email_address = request.POST.get('account', OutlookService.ALLOWED_ACCOUNTS[0])
    
    if not email_ids:
        return JsonResponse({'success': False, 'error': 'No emails selected'})
    
    # Check for VBA email IDs
    vba_ids = [email_id for email_id in email_ids if email_id.startswith('vba_')]
    com_ids = [email_id for email_id in email_ids if not email_id.startswith('vba_')]
    
    if vba_ids and not com_ids:
        return JsonResponse({
            'success': False, 
            'error': 'Cannot delete emails from VBA cache. Please wait for the next refresh or use Outlook directly.'
        })
    elif vba_ids and com_ids:
        return JsonResponse({
            'success': False, 
            'error': f'Cannot delete mixed email sources. {len(vba_ids)} emails are from VBA cache and cannot be deleted via web interface.'
        })
    
    try:
        # Connect to Outlook and delete the emails
        outlook = OutlookService()
        deleted_count = 0
        errors = []
        
        for email_id in com_ids:
            try:
                success = outlook.delete_email(email_address, email_id)
                if success:
                    deleted_count += 1
                else:
                    errors.append(f"Failed to delete email {email_id}")
            except Exception as e:
                errors.append(f"Error deleting email {email_id}: {str(e)}")
        
        if deleted_count == len(com_ids):
            return JsonResponse({'success': True, 'count': deleted_count})
        elif deleted_count > 0:
            return JsonResponse({
                'success': True,
                'partial': True,
                'count': deleted_count,
                'total': len(com_ids),
                'errors': errors
            })
        else:
            return JsonResponse({'success': False, 'error': 'Failed to delete any emails', 'errors': errors})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@restrict_read_only_users
def inbox_categorize_message(request, message_id):
    """
    Apply a category to a specific email message.
    """
    return JsonResponse({
        'success': False, 
        'message': 'Category functionality has been disabled. Please use external labeling system.'
    })


@csrf_exempt
@restrict_read_only_users
def inbox_categorize(request):
    """
    Apply a category to multiple email messages.
    """
    return JsonResponse({
        'success': False, 
        'error': 'Category functionality has been disabled. Please use external labeling system.'
    })


# Additional inbox views for reply and forward functionality
@login_required
@restrict_read_only_users
def inbox_reply(request, message_id):
    """
    Reply to an email message.
    """
    from ..services.outlook_service import OutlookService
    
    # Get email address from query params
    email_address = request.GET.get('account', OutlookService.ALLOWED_ACCOUNTS[0])
    
    # Create the reply form
    context = {
        'page_title': _('Reply to Email'),
        'email_address': email_address,
        'allowed_accounts': OutlookService.ALLOWED_ACCOUNTS,
        'is_reply': True,
    }
    
    # Only allow IRM account - no fallbacks
    if email_address not in OutlookService.ALLOWED_ACCOUNTS:
        messages.error(request, _(f"Access denied: Only {OutlookService.ALLOWED_ACCOUNTS[0]} is allowed."))
        context['access_denied'] = True
        return render(request, 'normieapp/inbox_compose.html', context)
    
    try:
        # Connect to Outlook and get the original email
        outlook = OutlookService()
        email = outlook.get_email(email_address, message_id)
        
        if not email:
            messages.error(request, _('Original email not found.'))
            return redirect('inbox')
        
        # Prepare reply fields
        context['to'] = email.get('sender_email', '')
        context['subject'] = f"RE: {email.get('subject', '')}"
        
        # Prepare reply body with original message
        reply_body = f"\n\n\n-----Original Message-----\n"
        reply_body += f"From: {email.get('sender', '')}\n"
        reply_body += f"Sent: {email.get('received_time', '')}\n"
        reply_body += f"To: {email.get('to', '')}\n"
        
        if email.get('cc'):
            reply_body += f"Cc: {email.get('cc')}\n"
            
        reply_body += f"Subject: {email.get('subject', '')}\n\n"
        reply_body += email.get('body', '')
        
        context['body'] = reply_body
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('inbox')
    
    return render(request, 'normieapp/inbox_compose.html', context) 