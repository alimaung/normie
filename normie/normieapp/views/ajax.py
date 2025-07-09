from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


@require_http_methods(["GET"])
def check_username_availability(request):
    """
    AJAX endpoint to check if username is available
    """
    username = request.GET.get('username', '').strip()
    
    if not username:
        return JsonResponse({
            'available': False,
            'message': _('Username is required.'),
            'type': 'error'
        })
    
    # Check minimum length
    if len(username) < 4:
        return JsonResponse({
            'available': False,
            'message': _('Username must be at least 4 characters long.'),
            'type': 'error'
        })
    
    # Check maximum length
    if len(username) > 30:
        return JsonResponse({
            'available': False,
            'message': _('Username must be 30 characters or less.'),
            'type': 'error'
        })
    
    # Check for valid characters (letters, numbers, periods, underscores, hyphens)
    import re
    if not re.match(r'^[a-zA-Z0-9._-]+$', username):
        return JsonResponse({
            'available': False,
            'message': _('Username can only contain letters, numbers, periods (.), underscores (_), and hyphens (-).'),
            'type': 'error'
        })
    
    # Check if username exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'available': False,
            'message': _('This username is already taken.'),
            'type': 'error'
        })
    
    return JsonResponse({
        'available': True,
        'message': _('Username is available!'),
        'type': 'success'
    })


@require_http_methods(["GET"])
def check_email_availability(request):
    """
    AJAX endpoint to check if email is available
    """
    email = request.GET.get('email', '').strip()
    
    if not email:
        return JsonResponse({
            'available': False,
            'message': _('Email is required.'),
            'type': 'error'
        })
    
    # Basic email format validation
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return JsonResponse({
            'available': False,
            'message': _('Please enter a valid email address.'),
            'type': 'error'
        })
    
    # Check if email exists
    if User.objects.filter(email=email).exists():
        return JsonResponse({
            'available': False,
            'message': _('This email address is already registered.'),
            'type': 'error'
        })
    
    return JsonResponse({
        'available': True,
        'message': _('Email is available!'),
        'type': 'success'
    }) 