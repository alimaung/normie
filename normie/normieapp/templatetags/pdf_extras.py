from django import template

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