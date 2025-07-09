from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext as _
from ..decorators import (
    admin_required, read_only_or_above_required
)
from ..models import UserProfile


def login_view(request):
    """
    Login page view.
    """
    # Check if user was redirected here due to login required
    next_url = request.GET.get('next')
    if next_url and not request.user.is_authenticated:
        messages.info(request, _(
            'Authentication Required: Please log in to access the requested page. '
            'If you don\'t have an account, you can create one with read-only access.'
        ))
    
    if request.method == 'POST':
        # Check if this is a signup form submission
        form_type = request.POST.get('form_type')
        
        if form_type == 'signup':
            # Handle signup
            from ..forms import SignUpForm
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, _('Account created successfully! You can now log in with read-only access.'))
                return redirect('login')
            else:
                # Add form errors to messages with better formatting
                for field, errors in form.errors.items():
                    field_name = field.replace('_', ' ').title()
                    if field == 'password1':
                        field_name = 'Password'
                    elif field == 'password2':
                        field_name = 'Confirm Password'
                    for error in errors:
                        messages.error(request, f'{field_name}: {error}')
        else:
            # Handle login
            username = request.POST.get('username')
            password = request.POST.get('password')
            remember_me = request.POST.get('remember_me')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Handle "Remember me" functionality
                if remember_me:
                    # Set session to expire in 30 days
                    request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days in seconds
                else:
                    # Set session to expire when browser closes
                    request.session.set_expiry(0)
                
                # Redirect to the originally requested page or home
                redirect_url = request.GET.get('next', 'home')
                return redirect(redirect_url)
            else:
                messages.error(request, _('Invalid username or password.'))
    
    return render(request, 'normieapp/login.html')


def signup_view(request):
    """
    User registration view.
    Creates new users with read-only permissions by default.
    """
    from ..forms import SignUpForm
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, _('Account created successfully! You can now log in with read-only access.'))
            return redirect('login')
    else:
        form = SignUpForm()
    
    context = {
        'form': form,
        'page_title': _('Create Account')
    }
    return render(request, 'normieapp/signup.html', context)


def logout_view(request):
    """
    Logout view.
    """
    logout(request)
    messages.success(request, _('Successfully logged out!'))
    return redirect('home')


@read_only_or_above_required
def profile(request):
    """
    User profile view - requires login with any role.
    """
    context = {
        'page_title': _('User Profile'),
        'user_info': {
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'date_joined': request.user.date_joined,
            'last_login': request.user.last_login,
        }
    }
    return render(request, 'normieapp/profile.html', context)


@read_only_or_above_required
def notifications(request):
    """
    Notifications view - requires login with any role.
    """
    context = {
        'page_title': _('Notifications'),
        'notifications': [
            {'id': 1, 'title': 'New material request', 'message': 'REQ-001 requires your approval', 'type': 'info', 'timestamp': '2024-03-15 14:30'},
            {'id': 2, 'title': 'Low stock alert', 'message': 'Welding Rods below minimum threshold', 'type': 'warning', 'timestamp': '2024-03-15 12:15'},
            {'id': 3, 'title': 'Standard updated', 'message': 'ISO 9001:2015 has been updated to version 2.1', 'type': 'success', 'timestamp': '2024-03-15 10:45'},
        ]
    }
    return render(request, 'normieapp/notifications.html', context)


@read_only_or_above_required
def settings(request):
    """
    Settings page view - requires login with any role.
    """
    context = {
        'page_title': _('Settings'),
        'user_settings': {
            'language': 'en',
            'timezone': 'UTC',
            'notifications_email': True,
            'notifications_browser': True,
            'dark_mode': False,
        }
    }
    return render(request, 'normieapp/settings.html', context)


@admin_required
def user_management(request):
    """
    User management view - restricted to administrators only.
    """
    from django.core.paginator import Paginator
    
    users = User.objects.select_related('profile').all().order_by('username')
    
    # Handle role updates
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        
        if user_id and new_role:
            try:
                user = User.objects.get(id=user_id)
                if hasattr(user, 'profile'):
                    user.profile.role = new_role
                    user.profile.save()
                    messages.success(request, f'Role updated for {user.username}')
                else:
                    UserProfile.objects.create(user=user, role=new_role)
                    messages.success(request, f'Profile created for {user.username}')
            except User.DoesNotExist:
                messages.error(request, 'User not found')
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': _('User Management'),
        'page_obj': page_obj,
        'role_choices': UserProfile.ROLE_CHOICES,
    }
    
    return render(request, 'normieapp/user_management.html', context)


@read_only_or_above_required
def user_profile_view(request):
    """
    User profile view - shows current user's profile and permissions, requires login with any role.
    """
    # Create profile if it doesn't exist
    if not hasattr(request.user, 'profile'):
        UserProfile.objects.create(user=request.user)
    
    # Get session information
    session_expiry = request.session.get_expiry_age()
    session_expires_at = request.session.get_expiry_date()
    is_extended_session = session_expiry > 1209600  # More than 2 weeks
    
    context = {
        'page_title': _('My Profile'),
        'profile': request.user.profile,
        'session_info': {
            'expiry_seconds': session_expiry,
            'expires_at': session_expires_at,
            'is_extended': is_extended_session,
            'expiry_days': round(session_expiry / 86400, 1) if session_expiry else 0,
        }
    }
    
    return render(request, 'normieapp/user_profile.html', context) 