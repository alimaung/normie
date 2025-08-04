from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
import logging
import json

from ..models import ContactMessage

logger = logging.getLogger(__name__)

@csrf_protect
@require_http_methods(["GET", "POST"])
def contact_view(request):
    """Handle contact form display and submission"""
    
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            department = request.POST.get('department', '').strip()
            subject = request.POST.get('subject', '').strip()
            message_text = request.POST.get('message', '').strip()
            
            # Validate required fields
            if not all([name, email, subject, message_text]):
                messages.error(request, _('Please fill in all required fields.'))
                return render(request, 'normieapp/contact.html')
            
            # Validate subject choice
            valid_subjects = [choice[0] for choice in ContactMessage.SUBJECT_CHOICES]
            if subject not in valid_subjects:
                messages.error(request, _('Please select a valid subject.'))
                return render(request, 'normieapp/contact.html')
            
            # Create contact message
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                department=department,
                subject=subject,
                message=message_text
            )
            
            logger.info(f"New contact message created: {contact_message.id} from {email}")
            
            # Send notification email to staff (optional)
            try:
                send_notification_email(contact_message)
            except Exception as e:
                logger.warning(f"Failed to send notification email: {e}")
            
            # Success message
            messages.success(request, _('Your message has been sent successfully. We will get back to you soon.'))
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': _('Your message has been sent successfully.')
                })
            
            return redirect('contact')
            
        except Exception as e:
            logger.error(f"Error processing contact form: {e}")
            messages.error(request, _('An error occurred while sending your message. Please try again.'))
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': _('An error occurred while sending your message.')
                })
    
    # GET request - display form
    return render(request, 'normieapp/contact.html')

@login_required
def contact_messages_inbox(request):
    """Handle contact messages in inbox view format"""
    
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 25))
        search = request.GET.get('search', '').strip()
        sort_by = request.GET.get('sort_by', 'created_at')
        sort_order = request.GET.get('sort_order', 'desc')
        message_id = request.GET.get('message_id')  # For single message view
        
        # Debug: Check total contact messages
        total_messages = ContactMessage.objects.count()
        logger.info(f"Contact messages inbox view - Total messages in DB: {total_messages}")
        
        # Handle single message view
        if message_id:
            try:
                contact_message = ContactMessage.objects.get(id=message_id)
                # Mark as read when viewed
                contact_message.mark_as_read()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.template.loader import render_to_string
                    
                    # Convert contact message to email-like format for the template
                    email_data = format_contact_message_as_email(contact_message)
                    
                    email_view_html = render_to_string(
                        'normieapp/includes/contact_message_view.html',
                        {'message': contact_message, 'email': email_data},
                        request=request
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'email_view': True,
                        'html': email_view_html,
                        'email': email_data
                    })
                    
            except ContactMessage.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Message not found'
                    })
                messages.error(request, _('Message not found'))
                return redirect('inbox')
        
        # Get contact messages with search and filtering (exclude archived/closed ones from main view)
        queryset = ContactMessage.objects.filter(
            status__in=['new', 'in_progress']
        )
        
        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(subject__icontains=search) |
                Q(message__icontains=search) |
                Q(department__icontains=search)
            )
        
        # Apply sorting
        sort_field = sort_by
        if sort_by == 'received_time':  # Map to contact message field
            sort_field = 'created_at'
        elif sort_by == 'sender_name':
            sort_field = 'name'
        
        if sort_order == 'desc':
            sort_field = f'-{sort_field}'
        
        queryset = queryset.order_by(sort_field)
        
        # Paginate results
        paginator = Paginator(queryset, per_page)
        contact_messages = paginator.get_page(page)
        
        # Convert contact messages to email-like format
        emails = []
        for msg in contact_messages:
            email_data = format_contact_message_as_email(msg)
            emails.append(email_data)
        
        logger.info(f"Converted {len(emails)} contact messages to email format")
        
        # Prepare pagination info
        try:
            page_range = list(paginator.get_elided_page_range(contact_messages.number, on_each_side=2, on_ends=1))
        except:
            page_range = [contact_messages.number] if contact_messages else [1]
            
        pagination_info = {
            'current_page': contact_messages.number if contact_messages else 1,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_previous': contact_messages.has_previous() if contact_messages else False,
            'has_next': contact_messages.has_next() if contact_messages else False,
            'start_index': contact_messages.start_index() if contact_messages else 0,
            'end_index': contact_messages.end_index() if contact_messages else 0,
            'page_range': page_range
        }
        
        # Get folder stats for contact messages
        folder_stats = get_contact_message_stats()
        
        # Prepare context for inbox template
        context = {
            'page_title': _('Contact Messages'),
            'emails': emails,
            'pagination': pagination_info,
            'folder_stats': folder_stats,
            'data_status': {'available': True, 'message': 'Contact messages loaded'},
            'current_filters': {
                'search': search,
                'folder': 'Contact',
                'sort_by': sort_by,
                'sort_order': sort_order
            },
            'current_folder': 'Contact',
            'per_page_options': [10, 25, 50, 100]
        }
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            logger.info(f"Returning AJAX response with {len(emails)} emails")
            return JsonResponse({
                'success': True,
                'emails': emails,
                'pagination': pagination_info,
                'folder_stats': folder_stats
            })
        
        return render(request, 'normieapp/inbox.html', context)
        
    except Exception as e:
        logger.error(f"Error loading contact messages: {str(e)}")
        messages.error(request, _('Error loading contact messages. Please try again.'))
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Failed to load contact messages'})
        
        return redirect('inbox')

@login_required
@require_http_methods(["POST"])
@csrf_protect
def contact_message_action(request):
    """Handle actions on contact messages (flag, status update, etc.)"""
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        action = data.get('action')
        
        if not message_id or not action:
            return JsonResponse({'success': False, 'error': 'Missing required parameters'})
            
        try:
            message = ContactMessage.objects.get(id=message_id)
        except ContactMessage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Message not found'})
        
        if action == 'flag':
            # Toggle flag status
            message.flagged = not message.flagged
            message.save()
            return JsonResponse({
                'success': True, 
                'flagged': message.flagged
            })
            
        elif action == 'mark_progress':
            message.status = 'in_progress'
            if not message.assigned_to:
                message.assigned_to = request.user
            message.save()
            return JsonResponse({'success': True, 'status': message.status})
            
        elif action == 'mark_resolved':
            message.status = 'resolved'
            message.save()
            return JsonResponse({'success': True, 'status': message.status})
            
        elif action == 'assign':
            message.assigned_to = request.user
            if message.status == 'new':
                message.status = 'in_progress'
            message.save()
            return JsonResponse({'success': True, 'assigned_to': request.user.get_full_name() or request.user.username})
            
        elif action == 'add_notes':
            notes = data.get('notes', '')
            message.internal_notes = notes
            message.save()
            return JsonResponse({'success': True})
            
        elif action == 'delete':
            message.delete()
            return JsonResponse({'success': True})
            
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        logger.error(f"Error in contact_message_action: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Server error'})

@login_required
def contact_messages_archived(request):
    """Get archived/processed contact messages"""
    try:
        # Get processed messages (resolved or closed)
        archived_messages = ContactMessage.objects.filter(
            status__in=['resolved', 'closed']
        ).order_by('-updated_at')
        
        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        paginator = Paginator(archived_messages, per_page)
        try:
            archived_page = paginator.page(page)
        except PageNotAnInteger:
            archived_page = paginator.page(1)
        except EmptyPage:
            archived_page = paginator.page(paginator.num_pages)
        
        # Format messages for display
        messages_data = []
        for msg in archived_page:
            messages_data.append({
                'id': str(msg.id),
                'subject': f"[{msg.get_subject_display()}] {msg.name}",
                'sender_name': msg.name,
                'sender_email': msg.email,
                'status': msg.status,
                'status_display': msg.get_status_display(),
                'updated_at': msg.updated_at.strftime('%Y-%m-%d %H:%M'),
                'assigned_to': msg.assigned_to.get_full_name() if msg.assigned_to else None
            })
        
        return JsonResponse({
            'success': True,
            'messages': messages_data,
            'pagination': {
                'current_page': archived_page.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': archived_page.has_previous(),
                'has_next': archived_page.has_next(),
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching archived messages: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Server error'})

def format_contact_message_as_email(contact_message):
    """Convert ContactMessage to email-like format for inbox display"""
    return {
        'id': str(contact_message.id),
        'subject': f"[{contact_message.get_subject_display()}] Contact Form Message",
        'sender_name': contact_message.name,
        'sender_email': contact_message.email,
        'body': contact_message.message,
        'received_time': contact_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'unread': contact_message.is_unread,
        'flagged': contact_message.flagged,
        'attachments': [],  # Contact messages don't have attachments
        'categories': contact_message.get_subject_display(),
        'folder': 'Contact',
        'message_type': 'contact',
        'department': contact_message.department or '',  # Ensure no None values
        'status': contact_message.status,
        'status_display': contact_message.get_status_display()
    }

def get_contact_message_stats():
    """Get statistics for contact messages"""
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(status='new').count()
    in_progress_messages = ContactMessage.objects.filter(status='in_progress').count()
    resolved_messages = ContactMessage.objects.filter(status='resolved').count()
    
    return {
        'folder_counts': {
            'Contact': total_messages,
            'Inbox': 0,  # Keep other folders at 0 for contact view
            'Sent Items': 0,
            'Drafts': 0,
            'Deleted Items': 0,
            'Outbox': 0
        },
        'total_emails': total_messages,
        'unread_emails': unread_messages,
        'important_emails': resolved_messages,  # Treat resolved as important
        'emails_with_attachments': 0  # Contact messages don't have attachments
    }

def send_notification_email(contact_message):
    """Send notification email to staff about new contact message"""
    
    try:
        subject = f"New Contact Message: {contact_message.get_subject_display()}"
        
        message_body = f"""
New contact message received:

From: {contact_message.name} ({contact_message.email})
Department: {contact_message.department or 'Not specified'}
Subject: {contact_message.get_subject_display()}
Date: {contact_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Message:
{contact_message.message}

---
View in admin: /admin/normieapp/contactmessage/{contact_message.id}/change/
        """
        
        # Send to configured staff email
        recipient_email = getattr(settings, 'CONTACT_NOTIFICATION_EMAIL', 'irm-standardization-office@rolls-royce.com')
        
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        
        logger.info(f"Notification email sent for contact message {contact_message.id}")
        
    except Exception as e:
        logger.error(f"Failed to send notification email: {e}")
        raise
