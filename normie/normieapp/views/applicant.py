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
from ..decorators import restrict_read_only_users

# Configure logger
logger = logging.getLogger(__name__)


@restrict_read_only_users
def applicant_state_parser(request):
    """
    Applicant State Parser page view - requires applicant role or above.
    Tool for parsing and analyzing applicant status data.
    """
    context = {
        'page_title': _('Applicant State Parser'),
        'description': _('Parse and analyze applicant status data from various sources'),
    }
    return render(request, 'normieapp/applicant_state_parser.html', context)


@restrict_read_only_users
def applicant_upload(request):
    """
    Handle applicant data file upload - requires applicant role or above.
    """
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        
        # Generate a unique ID for this form session
        form_id = str(uuid.uuid4())
        
        # Create temp directory if it doesn't exist
        base_dir = Path(__file__).resolve().parent.parent.parent
        temp_dir = os.path.join(base_dir, 'normieapp', 'static', 'normieapp', 'temp_forms')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the uploaded file temporarily
        file_path = os.path.join(temp_dir, f"{form_id}.pdf")
        with open(file_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
        
        # Parse PDF fields
        try:
            # Use PDF service for PDF files
            from ..services import pdf_service
            logger.info(f"Extracting fields from PDF: {pdf_file.name}")
            raw_fields = pdf_service.extract_pdf_fields(file_path)
            logger.info(f"Extracted {len(raw_fields)} raw fields from PDF")
            
            # Debug: Log raw fields
            for i, field in enumerate(raw_fields):
                logger.debug(f"Raw field {i+1}: id={field.get('id')}, name={field.get('name')}, type={field.get('type')}")
            
            # Filter to only applicant-related fields
            from .utils import filter_applicant_fields
            fields = filter_applicant_fields(raw_fields)
            logger.info(f"Filtered to {len(fields)} applicant-related fields")
            
            # Debug: Log filtered fields
            for i, field in enumerate(fields):
                logger.debug(f"Filtered field {i+1}: id={field.get('id')}, name={field.get('name')}, type={field.get('type')}")
            
            # Store fields in session for later use
            serializable_fields = json.loads(json.dumps(fields))
            
            request.session[f'applicant_form_{form_id}'] = {
                'fields': serializable_fields,
                'file_path': file_path,
                'original_filename': pdf_file.name
            }
            
            return redirect('applicant_editor', form_id=form_id)
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
            messages.error(request, f"Error processing PDF: {str(e)}")
            return redirect('applicant_state_parser')
    
    return redirect('applicant_state_parser')


@restrict_read_only_users
def applicant_editor(request, form_id):
    """
    Display applicant data editor - requires applicant role or above.
    """
    # Get form data from session
    form_data = request.session.get(f'applicant_form_{form_id}')
    
    if not form_data:
        messages.error(request, _("Form session expired or invalid."))
        return redirect('applicant_state_parser')
    
    fields = form_data.get('fields', [])
    original_filename = form_data.get('original_filename', 'unknown')
    
    return render(request, 'normieapp/applicant_editor.html', {
        'form_id': form_id,
        'fields': fields,
        'original_filename': original_filename
    })


@csrf_exempt
@restrict_read_only_users
def applicant_save(request, form_id):
    """
    Save edited applicant data - requires applicant role or above.
    """
    if request.method == 'POST':
        try:
            # Get form data from request
            form_data = json.loads(request.body)
            
            # Get original form data from session
            session_data = request.session.get(f'applicant_form_{form_id}')
            
            if not session_data:
                return JsonResponse({'success': False, 'message': _("Form session expired or invalid.")})
            
            # Update fields with new values
            fields = session_data.get('fields', [])
            for field in fields:
                if field['id'] in form_data:
                    field['value'] = form_data[field['id']]
            
            # Save updated fields back to session
            session_data['fields'] = fields
            request.session[f'applicant_form_{form_id}'] = session_data
            request.session.modified = True
            
            return JsonResponse({'success': True, 'message': _("Applicant data saved successfully.")})
        except Exception as e:
            print(f"Error saving applicant data: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': _("Invalid request method.")})


@restrict_read_only_users
def applicant_download(request, form_id):
    """
    Download the processed applicant data - requires applicant role or above.
    """
    # Get form data from session
    form_data = request.session.get(f'applicant_form_{form_id}')
    
    if not form_data:
        messages.error(request, _("Form session expired or invalid."))
        return redirect('applicant_state_parser')
    
    try:
        fields = form_data.get('fields', [])
        original_filename = form_data.get('original_filename', 'applicant_data')
        
        # Create JSON export of applicant data
        export_data = {
            'metadata': {
                'export_date': json.dumps(datetime.now(), default=str),
                'original_filename': original_filename,
                'total_fields': len(fields)
            },
            'applicant_data': {field['id']: field['value'] for field in fields}
        }
        
        # Create response
        response = HttpResponse(
            json.dumps(export_data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="applicant_data_{form_id}.json"'
        
        return response
    except Exception as e:
        messages.error(request, f"Error downloading data: {str(e)}")
        return redirect('applicant_editor', form_id=form_id) 