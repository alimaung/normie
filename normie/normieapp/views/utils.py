import json
import logging
import pandas as pd

# Configure logger
logger = logging.getLogger(__name__)


def filter_applicant_fields(raw_fields):
    """
    Take fields from positions 2 to 21 from the raw fields list.
    Ensures fields are properly sorted for display.
    """
    # Sort fields by ID using natural sort (ensures "2" comes before "10")
    def natural_sort_key(field):
        import re
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        field_id = field['id']
        return [convert(c) for c in re.split('([0-9]+)', str(field_id))]
    
    # Sort the raw fields first
    sorted_fields = sorted(raw_fields, key=natural_sort_key)
    
    # Log the sorted fields for debugging
    logger.info(f"Total fields after sorting: {len(sorted_fields)}")
    for i, field in enumerate(sorted_fields):
        logger.debug(f"Sorted field {i+1}: id={field.get('id')}, name={field.get('name')}, type={field.get('type')}")
    
    # Take fields from positions 2 to 21 (if available)
    start_idx = 1  # 0-indexed, so position 2 is index 1
    end_idx = min(21, len(sorted_fields))  # Don't go beyond the available fields
    
    # Handle case where there are fewer than 2 fields
    if start_idx >= len(sorted_fields):
        return []
    
    # Get the fields from positions 2 to 21
    filtered_fields = sorted_fields[start_idx:end_idx]
    
    # Log the filtered fields for debugging
    logger.info(f"Selected fields from positions 2-21: {len(filtered_fields)}")
    for i, field in enumerate(filtered_fields):
        logger.debug(f"Selected field {i+1}: id={field.get('id')}, name={field.get('name')}, type={field.get('type')}")
    
    return filtered_fields


def parse_spreadsheet_applicant_data(file_path):
    """
    Parse CSV/Excel files for applicant data.
    """
    try:
        # Read the file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        fields = []
        # Convert first row to fields (assuming first row contains applicant data)
        if not df.empty:
            for column in df.columns:
                value = df.iloc[0][column] if not df.empty else ""
                fields.append({
                    'id': column.lower().replace(' ', '_'),
                    'name': column,
                    'type': '/Tx',  # Text field
                    'value': str(value) if pd.notna(value) else ""
                })
        
        return fields
    except Exception as e:
        raise ValueError(f"Error parsing spreadsheet: {str(e)}")


def parse_json_applicant_data(file_path):
    """
    Parse JSON files for applicant data.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        fields = []
        # Flatten JSON data into fields
        def flatten_dict(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        if isinstance(data, dict):
            flattened = flatten_dict(data)
            for key, value in flattened.items():
                fields.append({
                    'id': key.lower(),
                    'name': key.replace('_', ' ').title(),
                    'type': '/Tx',  # Text field
                    'value': str(value) if value is not None else ""
                })
        elif isinstance(data, list) and data:
            # Use first item if it's a list
            first_item = data[0]
            if isinstance(first_item, dict):
                for key, value in first_item.items():
                    fields.append({
                        'id': key.lower(),
                        'name': key.replace('_', ' ').title(),
                        'type': '/Tx',  # Text field
                        'value': str(value) if value is not None else ""
                    })
        
        return fields
    except Exception as e:
        raise ValueError(f"Error parsing JSON: {str(e)}")


def get_next_possible_statuses(current_status, user):
    """
    Determine which status transitions are allowed for the current user.
    """
    user_groups = user.groups.values_list('name', flat=True)
    
    transitions = {
        'draft': ['submitted'],
        'submitted': ['chemscan_pending', 'rejected'],
        'chemscan_pending': ['chemscan_completed', 'requires_modification'] if 'ChemScan' in user_groups else [],
        'chemscan_completed': ['environmental_review'],
        'environmental_review': ['manufacturing_lab_review', 'rejected'] if 'Environmental' in user_groups else [],
        'manufacturing_lab_review': ['standards_office_review', 'requires_modification'] if 'Manufacturing Lab' in user_groups else [],
        'standards_office_review': ['approved', 'rejected'] if 'Standards Office' in user_groups else [],
        'requires_modification': ['submitted'],
        'approved': [],
        'rejected': []
    }
    
    return transitions.get(current_status, []) 