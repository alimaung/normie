from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def clean_html_email(html_content):
    """
    Clean HTML email content for better display.
    Light processing to improve readability without breaking existing HTML.
    """
    if not html_content:
        return ""
    
    # Convert the content to string if it's not already
    content = str(html_content)
    
    # Only do minimal processing to avoid breaking existing HTML
    # Convert plain text line breaks to HTML breaks, but only if no HTML structure exists
    if '<p>' not in content.lower() and '<br' not in content.lower() and '<div>' not in content.lower():
        # This looks like plain text, convert line breaks
        content = content.replace('\n', '<br>')
    
    # Convert bare URLs to clickable links only if they're not already in HTML
    # Simple pattern that won't conflict with existing HTML
    if '<a ' not in content.lower():
        # Only convert URLs if there are no existing links
        url_pattern = r'\b(https?://[^\s<>"]+)'
        content = re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', content)
    
    return mark_safe(content)

@register.filter
def email_preview(text, length=150):
    """
    Create a preview of email text, truncating at word boundaries.
    """
    if not text:
        return ""
    
    text = str(text)
    # Remove HTML tags for preview
    text = re.sub(r'<[^>]+>', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) <= length:
        return text
    
    # Truncate at word boundary
    truncated = text[:length]
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + "..." 