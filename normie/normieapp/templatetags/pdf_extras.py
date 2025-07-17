from django import template
from django.utils.safestring import mark_safe
import json
from datetime import datetime

register = template.Library()

@register.filter
def get_signature_info(signature_details, field_id):
    """
    Get signature information for a specific field ID.
    Usage: {{ signature_details|get_signature_info:field.id }}
    """
    if not signature_details or not field_id:
        return None
    return signature_details.get(field_id, None)

@register.filter
def dict_get(dictionary, key):
    """
    Get value from dictionary by key.
    Usage: {{ my_dict|dict_get:key }}
    """
    if not dictionary or not key:
        return None
    return dictionary.get(key, None)

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a key."""
    return dictionary.get(key)



@register.filter
def parse_datetime(date_string):
    """
    Parse datetime string to datetime object for Django date filters.
    Usage: {{ email.received_time|parse_datetime|date:"M d, H:i" }}
    """
    if not date_string:
        return None
    
    try:
        # Handle the format from VBA/JSON: "2025-07-14 09:02:31"
        if isinstance(date_string, str):
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        # If it's already a datetime object, return as-is
        return date_string
    except (ValueError, TypeError):
        # If parsing fails, return None so template can handle gracefully
        return None

@register.filter
def field_type_class(field_type):
    """Convert field type to CSS class."""
    if field_type == '/Tx':
        return 'text-field'
    elif field_type == '/Btn':
        return 'button-field'
    elif field_type == '/Sig':
        return 'signature-field'
    return 'unknown-field'

@register.filter
def is_button_field(field):
    """Check if field is a button field."""
    return field.get('dict_type') == 'btn' or field.get('type') == '/Btn'

@register.filter
def is_text_field(field):
    """Check if field is a text field."""
    return field.get('dict_type') == 'text' or field.get('type') == '/Tx'

@register.filter
def is_signature_field(field):
    """Check if field is a signature field."""
    return field.get('dict_type') == 'sig' or field.get('type') == '/Sig'

@register.filter
def is_long_text_field(field_id):
    """Check if field should be displayed as textarea."""
    long_text_fields = ['10', '19', '31', '38', '46', '49', '52']
    return field_id in long_text_fields

@register.filter
def is_date_field(field_id):
    """Check if field should be displayed with a date picker."""
    date_fields = ['2b', '21', '22a1', '22b1', '25c', '32c', '40c', '47c', '50c']
    return field_id in date_fields

@register.filter
def is_disabled_field(field_id):
    """Check if field should be disabled/grayed out."""
    disabled_fields = ['8', '22a', '22b']
    return field_id in disabled_fields

@register.filter
def is_combined_field(field_id):
    """Check if field is part of a combined field (checkbox + input)."""
    # Only checkbox + input combinations, NOT radio + input
    combined_fields = {
        '18d': '18e',  # checkbox + input
        '23a6': '23a1', '23a10': '23a2',  # ChemScan A checkboxes
        '24a5': '24a1', '24a6': '24a2', '24a7': '24a3',  # ChemScan A checkboxes
        '23b6': '23b1', '23b10': '23b2',  # ChemScan B checkboxes
        '24b5': '24b1', '24b6': '24b2', '24b7': '24b3',  # ChemScan B checkboxes
        # Manufacturing fields are radio + input, handled separately
    }
    return field_id in combined_fields

@register.filter
def is_radio_activation_field(field_id):
    """Check if field is a radio button that can activate an input field."""
    radio_activation_fields = {
        '39': '39a',   # "nicht möglich" activates input
        '41': '41a',   # "Mindesthaltbarkeit" activates input  
        '42': '42a',   # "Andere" activates input
        '44': '44a',   # "bereits eingetragen" activates input
        '48': '48a'    # "Andere" activates input
    }
    return field_id in radio_activation_fields

@register.filter
def get_radio_activation_input_field(field_id):
    """Get the input field ID for a radio activation field."""
    radio_activation_mapping = {
        '39': '39a',
        '41': '41a', 
        '42': '42a', 
        '44': '44a', 
        '48': '48a'
    }
    return radio_activation_mapping.get(field_id)

@register.filter
def get_radio_activation_values(field_id):
    """Get the radio values that should activate the input field."""
    activation_values = {
        '39': ['nicht möglich'],
        '41': ['Mindesthaltbarkeit'],
        '42': ['Andere'],
        '44': ['bereits eingetragen'],
        '48': ['Andere']
    }
    return activation_values.get(field_id, [])

@register.filter
def get_combined_input_field(field_id):
    """Get the input field ID for a combined checkbox field."""
    combined_mapping = {
        '18d': '18e',
        '23a6': '23a1', '23a10': '23a2',
        '24a5': '24a1', '24a6': '24a2', '24a7': '24a3',
        '23b6': '23b1', '23b10': '23b2',
        '24b5': '24b1', '24b6': '24b2', '24b7': '24b3',
        # Removed manufacturing fields - they're radio activation, not combined
    }
    return combined_mapping.get(field_id)

@register.filter
def is_hidden_input_field(field_id):
    """Check if field is a hidden input part of a combined or radio activation field."""
    hidden_input_fields = [
        '18e',  # Combined checkbox + input
        '23a1', '23a2', '24a1', '24a2', '24a3',  # ChemScan A 
        '23b1', '23b2', '24b1', '24b2', '24b3',  # ChemScan B
        '39a', '41a', '42a', '44a', '48a'  # Radio activation inputs
    ]
    return field_id in hidden_input_fields

@register.filter
def get_button_options(field):
    """Get button field options from the field data."""
    # This will be populated by the view with options from PDF_FIELD_DICT
    return field.get('options', [])

@register.filter
def is_field_in_section(field_id, section):
    """Check if a field belongs to a specific section."""
    sections = {
        'applicant': ['1', '2a', '2b', '2c', '2d', '3', '4', '5', '6', '7', '8', '9', 
                     '10', '11', '12a', '12b', '13', '14', '15a', '15b', '16', 
                     '17a', '17b', '17c', '18a', '18b', '18c', '18d', '18e', '19', '20', '21'],
        'chemscan_a': ['22a', '22a1', '22a2', '23a1', '23a2', '23a3', '23a4', '23a5', '23a6',
                      '23a7', '23a8', '23a9', '23a10', '23a11', '23a12', '23a13', '23a14',
                      '24a1', '24a2', '24a3', '24a4', '24a5', '24a6', '24a7', '24a8', 
                      '24a9', '24a10', '24a11'],
        'chemscan_b': ['22b', '22b1', '22b2', '23b1', '23b2', '23b3', '23b4', '23b5', '23b6',
                      '23b7', '23b8', '23b9', '23b10', '23b11', '23b12', '23b13', '23b14',
                      '24b1', '24b2', '24b3', '24b4', '24b5', '24b6', '24b7', '24b8', 
                      '24b9', '24b10', '24b11'],
        'environment': ['25a', '25b', '25c', '26', '27', '28', '29', '30', '31'],
        'health_safety': ['32a', '32b', '32c', '33', '34', '35', '36', '37', '38'],
        'manufacturing': ['39', '39a', '40a', '40b', '40c', '41', '41a', '42', '42a', 
                         '43', '44', '44a', '45', '46', '47a', '47b', '47c', '48', '48a', '49'],
        'standards': ['50a', '50b', '50c', '51', '52']
    }
    return field_id in sections.get(section, [])

@register.filter
def get_fields_for_section(fields, section):
    """Get all fields for a specific section, excluding hidden combined fields."""
    section_fields = []
    for field in fields:
        field_id = field.get('id')
        if is_field_in_section(field_id, section) and not is_hidden_input_field(field_id):
            section_fields.append(field)
    return section_fields

@register.filter
def is_radio_button_field(field_id):
    """Check if field should be displayed as radio buttons."""
    radio_fields = ['5', '6', '13', '14', '15a', '15b', '22a2', '22b2', '26', '27', '28', 
                   '29', '30', '33', '34', '35', '36', '37', '39', '41', '42', '43', '44', '48']
    return field_id in radio_fields

@register.filter
def is_checkbox_field(field_id):
    """Check if field should be displayed as checkbox."""
    checkbox_fields = ['18a', '18b', '18c', '18d', '23a3', '23a4', '23a5', '23a6', '23a7', 
                      '23a8', '23a9', '23a10', '23a11', '23a12', '23a13', '23a14',
                      '23b3', '23b4', '23b5', '23b6', '23b7', '23b8', '23b9', '23b10', 
                      '23b11', '23b12', '23b13', '23b14', '24a4', '24a5', '24a6', '24a7',
                      '24a8', '24a9', '24a10', '24a11', '24b4', '24b5', '24b6', '24b7',
                      '24b8', '24b9', '24b10', '24b11']
    return field_id in checkbox_fields

@register.filter
def is_file_upload_field(field_id):
    """Check if field should have file upload functionality."""
    file_upload_fields = ['18a', '18b', '18c']
    return field_id in file_upload_fields

@register.filter
def get_file_upload_label(field_id):
    """Get the appropriate label for file upload fields."""
    labels = {
        '18a': 'EU-Sicherheitsdatenblatt (eSDB)',
        '18b': 'Technisches Datenblatt, Produktbeschreibung', 
        '18c': 'Gefährdungsbeurteilung'
    }
    return labels.get(field_id, 'Dokument')

def parse_checkbox_value(field_value):
    """Parse checkbox values to determine if checked."""
    if not field_value:
        return False
    
    # Handle different checkbox value formats
    checked_values = ['Ja', '/Ja', '/Yes', '/0', 'True', 'true', '1']
    return str(field_value) in checked_values

@register.simple_tag
def render_field_input(field, all_fields=None):
    """Render the appropriate input for a field based on its type and configuration."""
    field_id = field.get('id', '')
    field_value = field.get('value', '')
    field_type = field.get('dict_type', 'text')
    
    # Skip hidden combined/activation input fields - they'll be rendered with their parent
    if is_hidden_input_field(field_id):
        return ''
    
    disabled_attr = 'disabled' if is_disabled_field(field_id) else ''
    disabled_class = 'disabled-field' if is_disabled_field(field_id) else ''
    
    if field_type == 'text':
        if is_date_field(field_id):
            # Date field with calendar picker
            return mark_safe(f'''
                <div class="date-input-container">
                    <input type="text" class="field-value date-field {disabled_class}" name="{field_id}" 
                           value="{field_value}" data-field-id="{field_id}" {disabled_attr}
                           placeholder="DD.MM.YYYY">
                    <button type="button" class="date-picker-toggle" data-target="{field_id}" {disabled_attr}>
                        <i class="fas fa-calendar-alt"></i>
                    </button>
                </div>
            ''')
        elif is_long_text_field(field_id):
            return mark_safe(f'''
                <textarea class="field-value long-text {disabled_class}" name="{field_id}" 
                          data-field-id="{field_id}" {disabled_attr}>{field_value}</textarea>
            ''')
        else:
            return mark_safe(f'''
                <input type="text" class="field-value {disabled_class}" name="{field_id}" 
                       value="{field_value}" data-field-id="{field_id}" {disabled_attr}>
            ''')
    
    elif field_type == 'btn':
        # Handle combined checkbox + input fields
        if is_combined_field(field_id):
            input_field_id = get_combined_input_field(field_id)
            input_field = None
            input_value = ''
            
            # Find the corresponding input field
            if all_fields:
                for f in all_fields:
                    if f.get('id') == input_field_id:
                        input_field = f
                        input_value = f.get('value', '')
                        break
            
            checkbox_checked = 'checked' if parse_checkbox_value(field_value) else ''
            
            # Dynamic label for combined checkbox - don't show "Aktivieren" 
            if field_value and field_value not in ['Ja', '/Ja', '/Yes', '/0', 'Nein', '/Off', '/No', 'false', 'False']:
                checkbox_label = field_value
            else:
                # For activation fields, show nothing instead of "Aktivieren"
                checkbox_label = ''
            
            return mark_safe(f'''
                <div class="combined-field-container">
                    <div class="checkbox-container">
                        <input type="checkbox" class="combined-checkbox {disabled_class}" 
                               name="{field_id}" {checkbox_checked} data-field-id="{field_id}"
                               data-target-input="{input_field_id}" {disabled_attr}>
                        <label class="dynamic-label">{checkbox_label}</label>
                    </div>
                    <div class="input-container">
                        <input type="text" class="field-value combined-input {disabled_class}" 
                               name="{input_field_id}" value="{input_value}" 
                               data-field-id="{input_field_id}" {disabled_attr}
                               style="{'display: block' if checkbox_checked else 'display: none'}">
                    </div>
                </div>
            ''')
        
        # Handle radio activation fields
        elif is_radio_activation_field(field_id):
            input_field_id = get_radio_activation_input_field(field_id)
            activation_values = get_radio_activation_values(field_id)
            input_field = None
            input_value = ''
            
            # Find the corresponding input field
            if all_fields:
                for f in all_fields:
                    if f.get('id') == input_field_id:
                        input_field = f
                        input_value = f.get('value', '')
                        break
            
            options = field.get('options', [])
            if options:
                # Check if current value should activate input
                should_show_input = field_value in activation_values
                
                # Radio button group with activation
                html = f'<div class="radio-activation-container">'
                html += f'<div class="radio-group {disabled_class}">'
                
                for display_text, pdf_value in options:
                    checked = 'checked' if field_value == display_text else ''
                    safe_id = pdf_value.replace('/', '').replace(' ', '_')
                    activates_input = display_text in activation_values
                    
                    html += f'''
                        <div class="radio-option">
                            <input type="radio" name="{field_id}" value="{display_text}" 
                                   id="{field_id}_{safe_id}" {checked} data-field-id="{field_id}"
                                   data-target-input="{input_field_id if activates_input else ''}"
                                   data-activation-value="{display_text if activates_input else ''}" {disabled_attr}>
                            <label for="{field_id}_{safe_id}">{display_text}</label>
                        </div>
                    '''
                
                html += '</div>'
                
                # Add the activation input field
                html += f'''
                    <div class="activation-input-container" style="margin-top: 10px;">
                        <input type="text" class="field-value activation-input {disabled_class}" 
                               name="{input_field_id}" value="{input_value}" 
                               data-field-id="{input_field_id}" {disabled_attr}
                               placeholder="Details eingeben..."
                               style="{'display: block' if should_show_input else 'display: none'}">
                    </div>
                '''
                
                html += '</div>'
                return mark_safe(html)
        
        # Regular radio buttons (no activation)
        options = field.get('options', [])
        if is_radio_button_field(field_id) and options:
            # Radio button group
            html = f'<div class="radio-group {disabled_class}">'
            for display_text, pdf_value in options:
                checked = 'checked' if field_value == display_text else ''
                safe_id = pdf_value.replace('/', '').replace(' ', '_')
                html += f'''
                    <div class="radio-option">
                        <input type="radio" name="{field_id}" value="{display_text}" 
                               id="{field_id}_{safe_id}" {checked} data-field-id="{field_id}" {disabled_attr}>
                        <label for="{field_id}_{safe_id}">{display_text}</label>
                    </div>
                '''
            html += '</div>'
            return mark_safe(html)
        else:
            # Regular checkbox - use dynamic text based on field value
            checked = 'checked' if parse_checkbox_value(field_value) else ''
            
            # Use the actual field value as display text, with fallback to Ja/Nein
            if field_value and field_value not in ['Ja', '/Ja', '/Yes', '/0', 'Nein', '/Off', '/No', 'false', 'False']:
                # Field has meaningful text content - use it as the label
                display_text = field_value
            else:
                # Field only has binary values - show Ja/Nein based on checked state
                display_text = 'Ja' if checked else 'Nein'
            
            # Check if this is a file upload field
            if is_file_upload_field(field_id):
                file_label = get_file_upload_label(field_id)
                return mark_safe(f'''
                    <div class="checkbox-container has-file-upload {disabled_class}">
                        <div style="display: flex; align-items: center; gap: 8px; flex-shrink: 0;">
                            <input type="checkbox" name="{field_id}" {checked} 
                                   data-field-id="{field_id}" class="file-upload-checkbox" {disabled_attr}>
                            <label class="dynamic-label">{display_text}</label>
                        </div>
                        <div class="file-upload-container" data-field-id="{field_id}">
                            <div class="files-grid" id="files-grid-{field_id}">
                                <div class="file-slot upload-slot" id="upload-slot-{field_id}">
                                    <div class="file-upload-area" onclick="document.getElementById('file-{field_id}').click()">
                                        <div class="file-upload-content">
                                            <div class="file-upload-icon">
                                                <i class="fas fa-cloud-upload-alt"></i>
                                            </div>
                                            <div class="file-upload-text">
                                                Datei hochladen
                                            </div>
                                            <div class="file-upload-hint">
                                                PDF, DOC, DOCX
                                            </div>
                                        </div>
                                    </div>
                                    <input type="file" id="file-{field_id}" class="file-upload-input" 
                                           accept=".pdf,.doc,.docx" data-field-id="{field_id}" multiple>
                                </div>
                            </div>
                        </div>
                    </div>
                ''')
            else:
                return mark_safe(f'''
                    <div class="checkbox-container {disabled_class}">
                        <input type="checkbox" name="{field_id}" {checked} 
                               data-field-id="{field_id}" {disabled_attr}>
                        <label class="dynamic-label">{display_text}</label>
                    </div>
                ''')
    
    elif field_type == 'sig':
        return mark_safe(f'''
            <div class="signature-indicator {disabled_class}">
                <i class="fas fa-signature"></i>
                {field_value if field_value else "Digital Signature"}
            </div>
        ''')
    
    else:
        # Fallback
        return mark_safe(f'''
            <input type="text" class="field-value {disabled_class}" name="{field_id}" 
                   value="{field_value}" data-field-id="{field_id}" {disabled_attr}>
        ''') 