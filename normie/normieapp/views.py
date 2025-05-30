from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home(request):
    """
    Home page view for the Normie standards and material management system.
    """
    return render(request, 'normieapp/home.html')


def standards(request):
    """
    Standards management view.
    """
    context = {
        'page_title': _('Standards Management'),
        'standards': [
            {'id': 1, 'name': 'ISO 9001:2015', 'status': 'Active', 'version': '2.1', 'last_updated': '2024-01-15'},
            {'id': 2, 'name': 'ISO 14001:2015', 'status': 'Under Review', 'version': '1.3', 'last_updated': '2024-02-20'},
            {'id': 3, 'name': 'OHSAS 18001', 'status': 'Draft', 'version': '1.0', 'last_updated': '2024-03-10'},
        ]
    }
    return render(request, 'normieapp/standards.html', context)


def requests(request):
    """
    Material requests view.
    """
    context = {
        'page_title': _('Material Requests'),
        'requests': [
            {'id': 'REQ-001', 'material': 'Steel Pipes', 'quantity': 50, 'status': 'Pending', 'requested_by': 'John Doe', 'date': '2024-03-15'},
            {'id': 'REQ-002', 'material': 'Safety Helmets', 'quantity': 25, 'status': 'Approved', 'requested_by': 'Jane Smith', 'date': '2024-03-14'},
            {'id': 'REQ-003', 'material': 'Welding Rods', 'quantity': 100, 'status': 'In Progress', 'requested_by': 'Mike Johnson', 'date': '2024-03-13'},
        ]
    }
    return render(request, 'normieapp/requests.html', context)


def materials(request):
    """
    Materials catalog view.
    """
    context = {
        'page_title': _('Materials Catalog'),
        'materials': [
            {'id': 'MAT-001', 'name': 'Steel Pipes', 'category': 'Construction', 'unit': 'meters', 'stock': 150, 'min_stock': 50},
            {'id': 'MAT-002', 'name': 'Safety Helmets', 'category': 'Safety', 'unit': 'pieces', 'stock': 75, 'min_stock': 20},
            {'id': 'MAT-003', 'name': 'Welding Rods', 'category': 'Tools', 'unit': 'kg', 'stock': 25, 'min_stock': 30},
            {'id': 'MAT-004', 'name': 'Concrete Mix', 'category': 'Construction', 'unit': 'bags', 'stock': 200, 'min_stock': 100},
        ]
    }
    return render(request, 'normieapp/materials.html', context)


def releases(request):
    """
    Release management view.
    """
    context = {
        'page_title': _('Release Management'),
        'releases': [
            {'id': 'REL-001', 'material': 'Steel Pipes', 'quantity': 30, 'status': 'Completed', 'released_to': 'Project Alpha', 'date': '2024-03-12'},
            {'id': 'REL-002', 'material': 'Safety Helmets', 'quantity': 15, 'status': 'Pending', 'released_to': 'Project Beta', 'date': '2024-03-15'},
            {'id': 'REL-003', 'material': 'Welding Rods', 'quantity': 50, 'status': 'In Transit', 'released_to': 'Project Gamma', 'date': '2024-03-14'},
        ]
    }
    return render(request, 'normieapp/releases.html', context)


def approvals(request):
    """
    Approval workflows view.
    """
    context = {
        'page_title': _('Approval Workflows'),
        'approvals': [
            {'id': 'APP-001', 'type': 'Material Request', 'item': 'REQ-001', 'status': 'Pending Manager', 'submitted_by': 'John Doe', 'date': '2024-03-15'},
            {'id': 'APP-002', 'type': 'Standard Update', 'item': 'ISO 9001:2015', 'status': 'Pending Review', 'submitted_by': 'Quality Team', 'date': '2024-03-14'},
            {'id': 'APP-003', 'type': 'Release Authorization', 'item': 'REL-002', 'status': 'Approved', 'submitted_by': 'Jane Smith', 'date': '2024-03-13'},
        ]
    }
    return render(request, 'normieapp/approvals.html', context)


def inventory(request):
    """
    Inventory management view.
    """
    context = {
        'page_title': _('Inventory Management'),
        'inventory_stats': {
            'total_items': 4,
            'low_stock_items': 1,
            'total_value': 45750,
            'last_updated': '2024-03-15 14:30'
        },
        'low_stock_items': [
            {'name': 'Welding Rods', 'current_stock': 25, 'min_stock': 30, 'status': 'Low Stock'},
        ]
    }
    return render(request, 'normieapp/inventory.html', context)


def reports(request):
    """
    Reports and analytics view.
    """
    context = {
        'page_title': _('Reports & Analytics'),
        'reports': [
            {'name': 'Monthly Material Usage', 'type': 'Usage Report', 'last_generated': '2024-03-01', 'status': 'Available'},
            {'name': 'Standards Compliance', 'type': 'Compliance Report', 'last_generated': '2024-02-28', 'status': 'Available'},
            {'name': 'Inventory Valuation', 'type': 'Financial Report', 'last_generated': '2024-03-15', 'status': 'Available'},
            {'name': 'Approval Metrics', 'type': 'Performance Report', 'last_generated': '2024-03-10', 'status': 'Generating'},
        ]
    }
    return render(request, 'normieapp/reports.html', context)


def audit(request):
    """
    Audit trail view.
    """
    context = {
        'page_title': _('Audit Trail'),
        'audit_logs': [
            {'timestamp': '2024-03-15 14:30:25', 'user': 'john.doe', 'action': 'Created material request', 'details': 'REQ-001 for Steel Pipes'},
            {'timestamp': '2024-03-15 13:45:12', 'user': 'jane.smith', 'action': 'Approved release', 'details': 'REL-003 for Welding Rods'},
            {'timestamp': '2024-03-15 12:20:08', 'user': 'admin', 'action': 'Updated standard', 'details': 'ISO 9001:2015 version 2.1'},
            {'timestamp': '2024-03-15 11:15:33', 'user': 'mike.johnson', 'action': 'Inventory update', 'details': 'Added 50 Safety Helmets'},
        ]
    }
    return render(request, 'normieapp/audit.html', context)


def settings(request):
    """
    Settings page view.
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


def login_view(request):
    """
    Login page view.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, _('Successfully logged in!'))
            return redirect('home')
        else:
            messages.error(request, _('Invalid username or password.'))
    
    return render(request, 'normieapp/login.html')


def logout_view(request):
    """
    Logout view.
    """
    logout(request)
    messages.success(request, _('Successfully logged out!'))
    return redirect('login')


@login_required
def profile(request):
    """
    User profile view.
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


def notifications(request):
    """
    Notifications view.
    """
    context = {
        'page_title': _('Notifications'),
        'notifications': [
            {'id': 1, 'type': 'warning', 'title': 'Low Stock Alert', 'message': 'Welding Rods are running low (25 remaining)', 'timestamp': '2024-03-15 14:30', 'read': False},
            {'id': 2, 'type': 'info', 'title': 'Request Approved', 'message': 'Your material request REQ-002 has been approved', 'timestamp': '2024-03-15 13:45', 'read': False},
            {'id': 3, 'type': 'success', 'title': 'Standard Updated', 'message': 'ISO 9001:2015 has been updated to version 2.1', 'timestamp': '2024-03-15 12:20', 'read': True},
            {'id': 4, 'type': 'info', 'title': 'New Release', 'message': 'Release REL-003 is ready for pickup', 'timestamp': '2024-03-15 11:15', 'read': True},
        ]
    }
    return render(request, 'normieapp/notifications.html', context) 