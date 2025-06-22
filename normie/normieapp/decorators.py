from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils.translation import gettext as _


def role_required(*roles):
    """
    Decorator that requires the user to have one of the specified roles.
    Usage: @role_required('admin', 'manager')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Check if user has a profile
            if not hasattr(request.user, 'profile'):
                messages.error(request, _('Your account is not properly configured. Please contact an administrator.'))
                return redirect('home')
            
            # Check if user has required role
            if request.user.profile.role in roles:
                return view_func(request, *args, **kwargs)
            else:
                role_names = [dict(request.user.profile.ROLE_CHOICES).get(role, role) for role in roles]
                role_list = ', '.join(role_names[:-1]) + (' or ' + role_names[-1] if len(role_names) > 1 else role_names[0] if role_names else '')
                messages.warning(request, _(
                    'Access Restricted: This page requires {} permissions. '
                    'Your current role is "{}". Please contact your administrator if you need access to this feature.'
                ).format(role_list, request.user.profile.get_role_display()))
                return redirect('home')
        
        return _wrapped_view
    return decorator


def permission_required(permission_name):
    """
    Decorator that requires the user to have a specific permission.
    Usage: @permission_required('can_view_reports')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Check if user has a profile
            if not hasattr(request.user, 'profile'):
                messages.error(request, _('Your account is not properly configured. Please contact an administrator.'))
                return redirect('home')
            
            # Check if user has the required permission
            if hasattr(request.user.profile, permission_name) and getattr(request.user.profile, permission_name):
                return view_func(request, *args, **kwargs)
            else:
                permission_display = permission_name.replace('can_', '').replace('_', ' ').title()
                messages.warning(request, _(
                    'Access Restricted: You need "{}" permission to access this feature. '
                    'Your current role is "{}". Please contact your administrator if you need access.'
                ).format(permission_display, request.user.profile.get_role_display()))
                return redirect('home')
        
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Decorator that requires admin role.
    """
    @wraps(view_func)
    @role_required('admin')
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def manager_or_admin_required(view_func):
    """
    Decorator that requires manager or admin role.
    """
    @wraps(view_func)
    @role_required('admin', 'manager')
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def can_edit_requests(view_func):
    """
    Decorator that checks if user can edit requests.
    """
    @wraps(view_func)
    @permission_required('can_edit_requests')
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def can_view_reports(view_func):
    """
    Decorator that checks if user can view reports.
    """
    @wraps(view_func)
    @permission_required('can_view_reports')
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def can_view_audit_logs(view_func):
    """
    Decorator that checks if user can view audit logs.
    """
    @wraps(view_func)
    @permission_required('can_view_audit_logs')
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def read_only_or_above_required(view_func):
    """
    Decorator that allows access for read-only users and above.
    Blocks access for users without proper roles.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has a profile
        if not hasattr(request.user, 'profile'):
            messages.error(request, _('Your account is not properly configured. Please contact an administrator.'))
            return redirect('home')
        
        # Allow access for all authenticated users with profiles
        # (since all roles including read_only should have access)
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def restrict_read_only_users(view_func):
    """
    Decorator that blocks access for read-only users.
    Only allows applicant role and above.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has a profile
        if not hasattr(request.user, 'profile'):
            messages.error(request, _('Your account is not properly configured. Please contact an administrator.'))
            return redirect('home')
        
        # Block read-only users with helpful message
        if request.user.profile.role == 'read_only':
            messages.warning(request, _(
                'Access Restricted: You have read-only permissions. '
                'To access this feature, please contact your administrator to upgrade your account permissions. '
                'You can still view your profile and browse the homepage.'
            ))
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def user_can_access_request(user, cmsr_request):
    """
    Helper function to check if a user can access a specific CMSR request.
    Returns True if user can access, False otherwise.
    """
    if not hasattr(user, 'profile'):
        return False
    
    profile = user.profile
    
    # Admins and managers can access all requests
    if profile.role in ['admin', 'manager'] or profile.can_view_all_requests:
        return True
    
    # Users can access their own requests
    if cmsr_request.applicant == user:
        return True
    
    # Specialists can access requests in their review stage
    if profile.role == 'chemscan_specialist' and cmsr_request.status in ['chemscan_pending', 'chemscan_completed']:
        return True
    
    if profile.role == 'environmental_reviewer' and cmsr_request.status == 'environmental_review':
        return True
    
    if profile.role == 'manufacturing_reviewer' and cmsr_request.status == 'manufacturing_lab_review':
        return True
    
    if profile.role == 'standards_officer' and cmsr_request.status == 'standards_office_review':
        return True
    
    return False


def user_can_edit_request(user, cmsr_request):
    """
    Helper function to check if a user can edit a specific CMSR request.
    """
    if not hasattr(user, 'profile'):
        return False
    
    profile = user.profile
    
    # Check basic edit permission
    if not profile.can_edit_requests:
        return False
    
    # Admins can edit any request
    if profile.role == 'admin':
        return True
    
    # Users can edit their own draft requests
    if cmsr_request.applicant == user and cmsr_request.status == 'draft':
        return True
    
    # Managers can edit requests in certain statuses
    if profile.role == 'manager' and cmsr_request.status in ['draft', 'submitted', 'requires_modification']:
        return True
    
    # Specialists can edit in their review stages
    if profile.role == 'chemscan_specialist' and cmsr_request.status in ['chemscan_pending']:
        return True
    
    if profile.role == 'environmental_reviewer' and cmsr_request.status == 'environmental_review':
        return True
    
    if profile.role == 'manufacturing_reviewer' and cmsr_request.status == 'manufacturing_lab_review':
        return True
    
    if profile.role == 'standards_officer' and cmsr_request.status == 'standards_office_review':
        return True
    
    return False 