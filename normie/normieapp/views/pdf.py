from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from pathlib import Path
import os
import json
import uuid
import logging
from datetime import datetime
from ..services import pdf_service
from ..decorators import admin_required

# Configure logger
logger = logging.getLogger(__name__)


@admin_required
def pdf_parser(request):
    """
    PDF parser page view - requires admin role.
    Central hub for PDF form processing and management.
    """
    context = {
        'page_title': _('PDF Parser'),
    }
    return render(request, 'normieapp/pdf_parser.html', context)


@admin_required
def pdf_upload(request):
    """
    Handle PDF form upload - requires admin role.
    """
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        
        # Generate a unique ID for this form session
        form_id = str(uuid.uuid4())
        
        # Create temp directory if it doesn't exist
        # Use a direct path instead of settings.BASE_DIR
        base_dir = Path(__file__).resolve().parent.parent.parent
        temp_dir = os.path.join(base_dir, 'normieapp', 'static', 'normieapp', 'temp_forms')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the uploaded file temporarily
        file_path = os.path.join(temp_dir, f"{form_id}.pdf")
        with open(file_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
        
        # Extract form fields
        try:
            fields = pdf_service.extract_pdf_fields(file_path)
            
            # Store fields in session for later use
            # Convert to JSON and back to ensure serialization works
            serializable_fields = json.loads(json.dumps(fields))
            
            request.session[f'pdf_form_{form_id}'] = {
                'fields': serializable_fields,
                'file_path': file_path
            }
            
            return redirect('pdf_editor', form_id=form_id)
        except Exception as e:
            messages.error(request, f"Error processing PDF: {str(e)}")
            return redirect('pdf_parser')
    
    return redirect('pdf_parser')


@admin_required
def pdf_editor(request, form_id):
    """
    Display PDF form editor - requires admin role.
    Enhanced to populate field options for proper German button field display.
    """
    # Get form data from session
    form_data = request.session.get(f'pdf_form_{form_id}')
    
    if not form_data:
        messages.error(request, _("Form session expired or invalid."))
        return redirect('pdf_parser')
    
    fields = form_data.get('fields', [])
    file_path = form_data.get('file_path')
    
    # Enhance fields with options for button fields
    for field in fields:
        field_id = field.get('id')
        if field_id and field.get('dict_type') == 'btn':
            # Get options from PDF_FIELD_DICT
            options = pdf_service.get_field_options(field_id)
            field['options'] = options
    
    # Get signature details if available
    signature_details = {}
    if file_path:
        try:
            signature_details = pdf_service.get_signature_details(file_path)
        except Exception as e:
            print(f"Could not extract signature details: {e}")
    
    return render(request, 'normieapp/pdf_form/pdf_form.html', {
        'form_id': form_id,
        'fields': fields,
        'signature_details': signature_details
    })


@csrf_exempt  # Add CSRF exemption for AJAX calls
@admin_required
def pdf_save(request, form_id):
    """
    Save edited PDF form fields back to the original PDF file - requires admin role.
    """
    if request.method == 'POST':
        try:
            # Get form data from request
            form_data = json.loads(request.body)
            
            # Get original form data from session
            session_data = request.session.get(f'pdf_form_{form_id}')
            
            if not session_data:
                return JsonResponse({'success': False, 'message': _("Form session expired or invalid.")})
            
            # Update fields with new values
            fields = session_data.get('fields', [])
            for field in fields:
                if field['id'] in form_data:
                    field['value'] = form_data[field['id']]
            
            # Get the original file path
            file_path = session_data.get('file_path')
            if not file_path or not os.path.exists(file_path):
                return JsonResponse({'success': False, 'message': _("Original PDF file not found.")})
            
            # Save changes back to the original PDF file
            try:
                pdf_service.save_pdf_changes(file_path, fields)
            except ImportError as import_error:
                return JsonResponse({'success': False, 'message': _("PyMuPDF is required for reliable PDF editing. Please install it with: pip install PyMuPDF")})
            except Exception as save_error:
                print(f"Error saving PDF: {save_error}")
                return JsonResponse({'success': False, 'message': _("Failed to save changes to PDF. The form fields may be corrupted or the file may be read-only.")})
            
            # Re-serialize to ensure JSON compatibility
            serializable_fields = json.loads(json.dumps(fields))
            
            # Save updated fields back to session
            session_data['fields'] = serializable_fields
            request.session[f'pdf_form_{form_id}'] = session_data
            request.session.modified = True  # Explicitly mark session as modified
            
            return JsonResponse({'success': True, 'message': _("Changes saved to the original document.")})
        except Exception as e:
            print(f"Error saving form: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': _("Invalid request method.")})


@admin_required
def pdf_download(request, form_id):
    """
    Download the updated PDF file (with saved changes) - requires admin role.
    Now uses <antragsnummer>_<tkz>.pdf format for filename.
    """
    # Get form data from session
    form_data = request.session.get(f'pdf_form_{form_id}')
    
    if not form_data:
        messages.error(request, _("Form session expired or invalid."))
        return redirect('pdf_parser')
    
    try:
        file_path = form_data.get('file_path')
        fields = form_data.get('fields', [])
        
        # Check if the original file exists
        if not file_path or not os.path.exists(file_path):
            messages.error(request, _("Original PDF file not found."))
            return redirect('pdf_editor', form_id=form_id)
        
        # Read the updated PDF file (which contains the saved changes)
        with open(file_path, 'rb') as f:
            pdf_content = f.read()
        
        # Extract Antragsnummer (field 1) and TKZ (field 51) for custom filename
        antragsnummer = ""
        tkz = ""
        
        for field in fields:
            field_id = field.get('id', '')
            field_value = field.get('value', '')
            
            if field_id == '1':  # Antragsnummer
                antragsnummer = str(field_value).strip()
            elif field_id == '51':  # Teilenummer (TKZ)
                tkz = str(field_value).strip()
        
        # Clean the values for use in filename (remove invalid characters)
        def clean_filename_part(text):
            import re
            # Remove or replace invalid filename characters
            text = re.sub(r'[<>:"/\\|?*]', '_', text)
            text = re.sub(r'\s+', '_', text)  # Replace spaces with underscores
            return text[:50]  # Limit length
        
        antragsnummer = clean_filename_part(antragsnummer)
        tkz = clean_filename_part(tkz)
        
        # Create custom filename
        if antragsnummer and tkz:
            download_filename = f"{antragsnummer}_{tkz}.pdf"
        elif antragsnummer:
            download_filename = f"{antragsnummer}.pdf"
        elif tkz:
            download_filename = f"TKZ_{tkz}.pdf"
        else:
            # Fallback to original logic
            original_filename = os.path.basename(file_path)
            if original_filename.endswith('.pdf'):
                base_name = original_filename[:-4]  # Remove .pdf extension
                download_filename = f"{base_name}_updated.pdf"
            else:
                download_filename = f"updated_form_{form_id}.pdf"
        
        # Check if this is a view request (inline) or download request
        is_view_request = request.GET.get('view') == '1'
        
        # Create response
        response = HttpResponse(pdf_content, content_type='application/pdf')
        
        if is_view_request:
            # For viewing: display inline in browser
            response['Content-Disposition'] = f'inline; filename="{download_filename}"'
        else:
            # For downloading: force download
            response['Content-Disposition'] = f'attachment; filename="{download_filename}"'
            response['Content-Type'] = 'application/octet-stream'  # Force download instead of inline viewing
        
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
    except Exception as e:
        messages.error(request, f"Error downloading PDF: {str(e)}")
        print(f"Error details: {e}")
        print(f"Form data: {form_data}")
        return redirect('pdf_editor', form_id=form_id)


@admin_required
def pdf_debug(request, form_id):
    """
    Debug view to inspect form data in the session - admin only.
    """
    form_data = request.session.get(f'pdf_form_{form_id}')
    
    if not form_data:
        return JsonResponse({'error': 'Form session not found'})
    
    # Get fields and ensure they have the correct structure
    fields = form_data.get('fields', [])
    file_path = form_data.get('file_path', '')
    
    # Return debug information
    debug_info = {
        'form_id': form_id,
        'file_path': file_path,
        'fields_count': len(fields),
        'fields_type': str(type(fields)),
        'fields': fields
    }
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2}) 