from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.conf import settings
import os
import json
import uuid
from .services import pdf_service
from pathlib import Path
from .decorators import (
    role_required, permission_required, admin_required, manager_or_admin_required,
    can_edit_requests, can_view_reports, can_view_audit_logs,
    user_can_access_request, user_can_edit_request, read_only_or_above_required,
    restrict_read_only_users
)
from .models import UserProfile


def home(request):
    """
    Home page view for the Normie standards and material management system.
    """
    return render(request, 'normieapp/home.html')

@restrict_read_only_users
def incoming(request):
    """
    Incoming page view - requires applicant role or above.
    """
    return render(request, 'normieapp/incoming.html')

@restrict_read_only_users
def directory(request):
    """
    Directory page view - requires applicant role or above.
    """
    return render(request, 'normieapp/directory.html')

@restrict_read_only_users
def chemscan(request):
    """
    ChemScan analysis and management view - requires applicant role or above.
    """
    context = {
        'page_title': _('ChemScan Analysis'),
        'analysis_stats': {
            'total_scans': 1247,
            'pending_review': 23,
            'approved_substances': 892,
            'flagged_substances': 15
        },
        'recent_scans': [
            {'id': 'CS-001', 'substance': 'Acetone', 'status': 'Approved', 'risk_level': 'Low', 'date': '2024-03-15'},
            {'id': 'CS-002', 'substance': 'Methylene Chloride', 'status': 'Flagged', 'risk_level': 'High', 'date': '2024-03-14'},
            {'id': 'CS-003', 'substance': 'Isopropanol', 'status': 'Pending', 'risk_level': 'Medium', 'date': '2024-03-13'},
            {'id': 'CS-004', 'substance': 'Toluene', 'status': 'Under Review', 'risk_level': 'Medium', 'date': '2024-03-12'},
        ]
    }
    return render(request, 'normieapp/chemscan.html', context)

@restrict_read_only_users
def standards(request):
    """
    Standards management view - requires applicant role or above.
    """
    context = {
        'page_title': _('Standards Management'),
        'standards': [
            {'id': 1, 'name': 'ISO 9001:2015', 'status': 'Active', 'version': '2.1', 'last_updated': '2024-01-15'},
            {'id': 2, 'name': 'ISO 14001:2015', 'status': 'Under Review', 'version': '1.3', 'last_updated': '2024-02-20'},
            {'id': 3, 'name': 'OHSAS 18001', 'status': 'Draft', 'version': '1.0', 'last_updated': '2024-03-10'},
        ]
    }
    return render(request, 'normieapp/prototyping/standards.html', context)


@restrict_read_only_users
def requests(request):
    """
    Material requests view - requires applicant role or above.
    """
    context = {
        'page_title': _('Material Requests'),
        'requests': [
            {'id': 'REQ-001', 'material': 'Steel Pipes', 'quantity': 50, 'status': 'Pending', 'requested_by': 'John Doe', 'date': '2024-03-15'},
            {'id': 'REQ-002', 'material': 'Safety Helmets', 'quantity': 25, 'status': 'Approved', 'requested_by': 'Jane Smith', 'date': '2024-03-14'},
            {'id': 'REQ-003', 'material': 'Welding Rods', 'quantity': 100, 'status': 'In Progress', 'requested_by': 'Mike Johnson', 'date': '2024-03-13'},
        ]
    }
    return render(request, 'normieapp/prototyping/requests.html', context)


@restrict_read_only_users
def materials(request):
    """
    Materials catalog view - requires applicant role or above.
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
    return render(request, 'normieapp/prototyping/materials.html', context)


@restrict_read_only_users
def releases(request):
    """
    Release management view - requires applicant role or above.
    """
    context = {
        'page_title': _('Release Management'),
        'releases': [
            {'id': 'REL-001', 'material': 'Steel Pipes', 'quantity': 30, 'status': 'Completed', 'released_to': 'Project Alpha', 'date': '2024-03-12'},
            {'id': 'REL-002', 'material': 'Safety Helmets', 'quantity': 15, 'status': 'Pending', 'released_to': 'Project Beta', 'date': '2024-03-15'},
            {'id': 'REL-003', 'material': 'Welding Rods', 'quantity': 50, 'status': 'In Transit', 'released_to': 'Project Gamma', 'date': '2024-03-14'},
        ]
    }
    return render(request, 'normieapp/prototyping/releases.html', context)


@manager_or_admin_required
def approvals(request):
    """
    Approval workflows view - restricted to managers and administrators.
    """
    context = {
        'page_title': _('Approval Workflows'),
        'approvals': [
            {'id': 'APP-001', 'type': 'Material Request', 'item': 'REQ-001', 'status': 'Pending Manager', 'submitted_by': 'John Doe', 'date': '2024-03-15'},
            {'id': 'APP-002', 'type': 'Standard Update', 'item': 'ISO 9001:2015', 'status': 'Pending Review', 'submitted_by': 'Quality Team', 'date': '2024-03-14'},
            {'id': 'APP-003', 'type': 'Release Authorization', 'item': 'REL-002', 'status': 'Approved', 'submitted_by': 'Jane Smith', 'date': '2024-03-13'},
        ]
    }
    return render(request, 'normieapp/prototyping/approvals.html', context)


@restrict_read_only_users
def inventory(request):
    """
    Inventory management view - requires applicant role or above.
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
    return render(request, 'normieapp/prototyping/inventory.html', context)


@can_view_reports
def reports(request):
    """
    Reports and analytics view - restricted to users with report viewing permissions.
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
    return render(request, 'normieapp/prototyping/reports.html', context)


@can_view_audit_logs
def audit(request):
    """
    Audit trail view - restricted to users with audit log viewing permissions.
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
    return render(request, 'normieapp/prototyping/audit.html', context)


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
    from .forms import SignUpForm
    
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


@restrict_read_only_users
def cmsr_request(request):
    """
    CMSR (Consumable Material Supply Request) form view - requires applicant role or above.
    Handles the complete multi-step approval workflow.
    """
    from .models import CMSRRequest, CMSRDocument
    from .forms import CMSRRequestForm, CMSRDocumentForm
    
    if request.method == 'POST':
        form = CMSRRequestForm(request.POST)
        if form.is_valid():
            cmsr = form.save(commit=False)
            cmsr.applicant = request.user
            cmsr.applicant_name = request.user.get_full_name() or request.user.username
            cmsr.save()
            
            # Handle document uploads
            for file in request.FILES.getlist('documents'):
                CMSRDocument.objects.create(
                    cmsr_request=cmsr,
                    document_type=request.POST.get('document_type', 'other'),
                    file=file,
                    filename=file.name,
                    uploaded_by=request.user
                )
            
            messages.success(request, _('CMSR request submitted successfully. Application number: {}').format(cmsr.application_number))
            return redirect('cmsr_detail', pk=cmsr.pk)
    else:
        form = CMSRRequestForm()
    
    context = {
        'page_title': _('Consumable Material Supply Request (CMSR)'),
        'form': form,
        'document_form': CMSRDocumentForm(),
        'help_text': {
            'introduction': _('Submit chemical substance and parts approval requests for industrial use.'),
            'process_info': _('This is a digital process following RRTI00032 guidelines.'),
            'search_info': _('Before submitting, search OMat Catalogue, MLC 104, and RRD Consumables Catalogue for existing approved materials.')
        }
    }
    return render(request, 'normieapp/prototyping/cmsr_request.html', context)


@restrict_read_only_users
def cmsr_detail(request, pk):
    """
    CMSR request detail view with workflow management - requires applicant role or above.
    """
    from .models import CMSRRequest, CMSRWorkflowLog
    
    cmsr = get_object_or_404(CMSRRequest, pk=pk)
    
    # Check permissions
    can_edit = (
        cmsr.applicant == request.user or 
        request.user.has_perm('normieapp.change_cmsrrequest') or
        request.user.groups.filter(name__in=['ChemScan', 'Environmental', 'Manufacturing Lab', 'Standards Office']).exists()
    )
    
    # Handle status updates
    if request.method == 'POST' and can_edit:
        new_status = request.POST.get('new_status')
        comments = request.POST.get('comments', '')
        
        if new_status and new_status != cmsr.status:
            # Log the workflow change
            CMSRWorkflowLog.objects.create(
                cmsr_request=cmsr,
                previous_status=cmsr.status,
                new_status=new_status,
                changed_by=request.user,
                comments=comments
            )
            
            cmsr.status = new_status
            cmsr.save()
            
            messages.success(request, _('Status updated to: {}').format(dict(CMSRRequest.STATUS_CHOICES)[new_status]))
            return redirect('cmsr_detail', pk=pk)
    
    context = {
        'page_title': f'CMSR {cmsr.application_number}',
        'cmsr': cmsr,
        'can_edit': can_edit,
        'workflow_logs': cmsr.workflow_logs.all()[:10],
        'documents': cmsr.documents.all(),
        'status_choices': CMSRRequest.STATUS_CHOICES,
        'next_possible_statuses': get_next_possible_statuses(cmsr.status, request.user)
    }
    return render(request, 'normieapp/prototyping/cmsr_detail.html', context)


@restrict_read_only_users
def cmsr_list(request):
    """
    List view for CMSR requests with filtering and search - requires applicant role or above.
    """
    from .models import CMSRRequest
    from django.db.models import Q
    
    queryset = CMSRRequest.objects.all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    # Filter by user's requests
    my_requests = request.GET.get('my_requests')
    if my_requests:
        queryset = queryset.filter(applicant=request.user)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        queryset = queryset.filter(
            Q(application_number__icontains=search_query) |
            Q(product_name__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(applicant_name__icontains=search_query)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': _('CMSR Requests'),
        'page_obj': page_obj,
        'status_choices': CMSRRequest.STATUS_CHOICES,
        'current_filters': {
            'status': status_filter,
            'my_requests': my_requests,
            'search': search_query
        }
    }
    return render(request, 'normieapp/prototyping/cmsr_list.html', context)


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


@restrict_read_only_users
def cmsr_edit(request, pk):
    """
    Edit CMSR request view - requires applicant role or above.
    """
    from .models import CMSRRequest
    from .forms import CMSRRequestForm
    
    cmsr = get_object_or_404(CMSRRequest, pk=pk)
    
    # Check permissions
    if cmsr.applicant != request.user and not request.user.has_perm('normieapp.change_cmsrrequest'):
        messages.error(request, _('You do not have permission to edit this request.'))
        return redirect('cmsr_detail', pk=pk)
    
    if request.method == 'POST':
        form = CMSRRequestForm(request.POST, instance=cmsr)
        if form.is_valid():
            form.save()
            messages.success(request, _('CMSR request updated successfully.'))
            return redirect('cmsr_detail', pk=pk)
    else:
        form = CMSRRequestForm(instance=cmsr)
    
    context = {
        'page_title': f'Edit CMSR {cmsr.application_number}',
        'form': form,
        'cmsr': cmsr
    }
    return render(request, 'normieapp/prototyping/cmsr_edit.html', context)


@role_required('admin', 'manager', 'chemscan_specialist')
def cmsr_chemscan(request, pk):
    """
    ChemScan assessment view for CMSR request - restricted to ChemScan specialists, managers, and admins.
    """
    from .models import CMSRRequest, ChemScanAssessment
    from .forms import ChemScanAssessmentForm
    
    cmsr = get_object_or_404(CMSRRequest, pk=pk)
    
    # Check if user can access this request
    if not user_can_access_request(request.user, cmsr):
        messages.error(request, _('You do not have permission to access this request.'))
        return redirect('cmsr_list')
    
    # Get or create ChemScan assessment
    chemscan, created = ChemScanAssessment.objects.get_or_create(cmsr_request=cmsr)
    
    # Check if user can perform ChemScan
    can_edit = request.user.profile.can_perform_chemscan
    
    if request.method == 'POST' and can_edit:
        form = ChemScanAssessmentForm(request.POST, instance=chemscan)
        if form.is_valid():
            form.save()
            messages.success(request, _('ChemScan assessment updated successfully.'))
            return redirect('cmsr_detail', pk=pk)
    else:
        form = ChemScanAssessmentForm(instance=chemscan)
    
    context = {
        'page_title': f'ChemScan Assessment - CMSR {cmsr.application_number}',
        'form': form,
        'cmsr': cmsr,
        'chemscan': chemscan,
        'can_edit': can_edit
    }
    return render(request, 'normieapp/prototyping/cmsr_chemscan.html', context)


@role_required('admin', 'manager', 'environmental_reviewer')
def cmsr_environmental(request, pk):
    """
    Environmental assessment view for CMSR request - restricted to environmental reviewers, managers, and admins.
    """
    from .models import CMSRRequest, EnvironmentalAssessment
    from .forms import EnvironmentalAssessmentForm
    
    cmsr = get_object_or_404(CMSRRequest, pk=pk)
    
    # Check if user can access this request
    if not user_can_access_request(request.user, cmsr):
        messages.error(request, _('You do not have permission to access this request.'))
        return redirect('cmsr_list')
    
    # Get or create Environmental assessment
    environmental, created = EnvironmentalAssessment.objects.get_or_create(cmsr_request=cmsr)
    
    if request.method == 'POST':
        form = EnvironmentalAssessmentForm(request.POST, instance=environmental)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.assessed_by = request.user
            assessment.save()
            messages.success(request, _('Environmental assessment updated successfully.'))
            return redirect('cmsr_detail', pk=pk)
    else:
        form = EnvironmentalAssessmentForm(instance=environmental)
    
    context = {
        'page_title': f'Environmental Assessment - CMSR {cmsr.application_number}',
        'form': form,
        'cmsr': cmsr,
        'environmental': environmental
    }
    return render(request, 'normieapp/prototyping/cmsr_environmental.html', context)


@role_required('admin', 'manager', 'manufacturing_reviewer')
def cmsr_manufacturing(request, pk):
    """
    Manufacturing lab approval view for CMSR request - restricted to manufacturing reviewers, managers, and admins.
    """
    from .models import CMSRRequest, ManufacturingLabApproval
    from .forms import ManufacturingLabApprovalForm
    
    cmsr = get_object_or_404(CMSRRequest, pk=pk)
    
    # Check if user can access this request
    if not user_can_access_request(request.user, cmsr):
        messages.error(request, _('You do not have permission to access this request.'))
        return redirect('cmsr_list')
    
    # Get or create Manufacturing lab approval
    manufacturing, created = ManufacturingLabApproval.objects.get_or_create(cmsr_request=cmsr)
    
    if request.method == 'POST':
        form = ManufacturingLabApprovalForm(request.POST, instance=manufacturing)
        if form.is_valid():
            form.save()
            messages.success(request, _('Manufacturing lab approval updated successfully.'))
            return redirect('cmsr_detail', pk=pk)
    else:
        form = ManufacturingLabApprovalForm(instance=manufacturing)
    
    context = {
        'page_title': f'Manufacturing Lab Approval - CMSR {cmsr.application_number}',
        'form': form,
        'cmsr': cmsr,
        'manufacturing': manufacturing
    }
    return render(request, 'normieapp/prototyping/cmsr_manufacturing.html', context)


@role_required('admin', 'manager', 'standards_officer')
def cmsr_standards(request, pk):
    """
    Standards office approval view for CMSR request - restricted to standards officers, managers, and admins.
    """
    from .models import CMSRRequest, StandardsOfficeApproval
    from .forms import StandardsOfficeApprovalForm
    
    cmsr = get_object_or_404(CMSRRequest, pk=pk)
    
    # Check if user can access this request
    if not user_can_access_request(request.user, cmsr):
        messages.error(request, _('You do not have permission to access this request.'))
        return redirect('cmsr_list')
    
    # Get or create Standards office approval
    standards, created = StandardsOfficeApproval.objects.get_or_create(cmsr_request=cmsr)
    
    if request.method == 'POST':
        form = StandardsOfficeApprovalForm(request.POST, instance=standards)
        if form.is_valid():
            form.save()
            messages.success(request, _('Standards office approval updated successfully.'))
            return redirect('cmsr_detail', pk=pk)
    else:
        form = StandardsOfficeApprovalForm(instance=standards)
    
    context = {
        'page_title': f'Standards Office Approval - CMSR {cmsr.application_number}',
        'form': form,
        'cmsr': cmsr,
        'standards': standards
    }
    return render(request, 'normieapp/prototyping/cmsr_standards.html', context)


@restrict_read_only_users
def cmsr_documents(request, pk):
    """
    Document management view for CMSR request - requires applicant role or above.
    """
    from .models import CMSRRequest, CMSRDocument
    from .forms import CMSRDocumentForm
    
    cmsr = get_object_or_404(CMSRRequest, pk=pk)
    
    # Check permissions
    can_edit = (
        cmsr.applicant == request.user or 
        request.user.has_perm('normieapp.change_cmsrrequest') or
        request.user.groups.filter(name__in=['ChemScan', 'Environmental', 'Manufacturing Lab', 'Standards Office']).exists()
    )
    
    if request.method == 'POST' and can_edit:
        form = CMSRDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.cmsr_request = cmsr
            document.uploaded_by = request.user
            document.filename = document.file.name
            document.save()
            messages.success(request, _('Document uploaded successfully.'))
            return redirect('cmsr_documents', pk=pk)
    else:
        form = CMSRDocumentForm()
    
    context = {
        'page_title': f'Documents - CMSR {cmsr.application_number}',
        'form': form,
        'cmsr': cmsr,
        'documents': cmsr.documents.all(),
        'can_edit': can_edit
    }
    return render(request, 'normieapp/prototyping/cmsr_documents.html', context)

@restrict_read_only_users
def pdf_upload(request):
    """
    Handle PDF form upload - requires applicant role or above.
    """
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        
        # Generate a unique ID for this form session
        form_id = str(uuid.uuid4())
        
        # Create temp directory if it doesn't exist
        # Use a direct path instead of settings.BASE_DIR
        base_dir = Path(__file__).resolve().parent.parent
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
            
            return redirect('pdf_edit', form_id=form_id)
        except Exception as e:
            messages.error(request, f"Error processing PDF: {str(e)}")
            return redirect('incoming')
    
    return redirect('incoming')

@restrict_read_only_users
def pdf_edit(request, form_id):
    """
    Display PDF form editor - requires applicant role or above.
    """
    # Get form data from session
    form_data = request.session.get(f'pdf_form_{form_id}')
    
    if not form_data:
        messages.error(request, _("Form session expired or invalid."))
        return redirect('incoming')
    
    fields = form_data.get('fields', [])
    file_path = form_data.get('file_path')
    
    # Get signature details if available
    signature_details = {}
    if file_path:
        try:
            signature_details = pdf_service.get_signature_details(file_path)
        except Exception as e:
            print(f"Could not extract signature details: {e}")
    
    return render(request, 'normieapp/pdf_form.html', {
        'form_id': form_id,
        'fields': fields,
        'signature_details': signature_details
    })

@csrf_exempt  # Add CSRF exemption for AJAX calls
@restrict_read_only_users
def pdf_save(request, form_id):
    """
    Save edited PDF form fields back to the original PDF file - requires applicant role or above.
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

@restrict_read_only_users
def pdf_download(request, form_id):
    """
    Download the updated PDF file (with saved changes) - requires applicant role or above.
    """
    # Get form data from session
    form_data = request.session.get(f'pdf_form_{form_id}')
    
    if not form_data:
        messages.error(request, _("Form session expired or invalid."))
        return redirect('incoming')
    
    try:
        file_path = form_data.get('file_path')
        
        # Check if the original file exists
        if not file_path or not os.path.exists(file_path):
            messages.error(request, _("Original PDF file not found."))
            return redirect('pdf_edit', form_id=form_id)
        
        # Read the updated PDF file (which contains the saved changes)
        with open(file_path, 'rb') as f:
            pdf_content = f.read()
        
        # Extract original filename for a better download name
        original_filename = os.path.basename(file_path)
        if original_filename.endswith('.pdf'):
            base_name = original_filename[:-4]  # Remove .pdf extension
            download_filename = f"{base_name}_updated.pdf"
        else:
            download_filename = f"updated_form_{form_id}.pdf"
        
        # Create response
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{download_filename}"'
        
        return response
    except Exception as e:
        messages.error(request, f"Error downloading PDF: {str(e)}")
        print(f"Error details: {e}")
        print(f"Form data: {form_data}")
        return redirect('pdf_edit', form_id=form_id)

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

@admin_required
def user_management(request):
    """
    User management view - restricted to administrators only.
    """
    from django.contrib.auth.models import User
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

def about(request):
    """
    About page - public access for guests.
    """
    context = {
        'page_title': _('About Normie'),
        'team_members': [
            {
                'name': 'Dr. Sarah Chen',
                'role': 'Chief Technology Officer',
                'description': 'Expert in standards management with 15+ years experience',
                'image_color': '#667eea'
            },
            {
                'name': 'Michael Rodriguez',
                'role': 'Head of Product',
                'description': 'Specializes in workflow optimization and user experience',
                'image_color': '#764ba2'
            },
            {
                'name': 'Anna Schmidt',
                'role': 'Compliance Director',
                'description': 'Regulatory compliance and quality assurance specialist',
                'image_color': '#f093fb'
            },
        ],
        'stats': {
            'years_experience': 12,
            'clients_served': 500,
            'standards_managed': 10000,
            'countries': 25
        }
    }
    return render(request, 'normieapp/about.html', context)


def contact(request):
    """
    Contact page - public access for guests.
    """
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you would typically send an email or save to database
        # For now, just show a success message
        messages.success(request, _('Thank you for your message! We will get back to you soon.'))
        return redirect('contact')
    
    context = {
        'page_title': _('Contact Us'),
        'office_locations': [
            {
                'city': 'Munich',
                'country': 'Germany',
                'address': 'Maximilianstraße 35, 80539 München',
                'phone': '+49 89 123 456 789',
                'email': 'munich@normie.de'
            },
            {
                'city': 'Frankfurt',
                'country': 'Germany', 
                'address': 'Zeil 106, 60313 Frankfurt am Main',
                'phone': '+49 69 987 654 321',
                'email': 'frankfurt@normie.de'
            }
        ]
    }
    return render(request, 'normieapp/contact.html', context)


def features_detail(request):
    """
    Detailed features page - public access for guests.
    """
    context = {
        'page_title': _('Features & Capabilities'),
        'feature_categories': [
            {
                'title': _('Standards Management'),
                'description': _('Comprehensive tools for creating, maintaining, and tracking organizational standards.'),
                'features': [
                    _('Version control and history tracking'),
                    _('Collaborative editing and review workflows'),
                    _('Automated compliance checking'),
                    _('Document templates and standardization'),
                    _('Integration with regulatory databases')
                ],
                'color': '#667eea'
            },
            {
                'title': _('Request Processing'),
                'description': _('Streamlined material request workflows with intelligent automation.'),
                'features': [
                    _('Smart form validation and auto-completion'),
                    _('Role-based approval routing'),
                    _('Real-time status tracking'),
                    _('Automated notifications and reminders'),
                    _('Integration with procurement systems')
                ],
                'color': '#764ba2'
            },
            {
                'title': _('Analytics & Reporting'),
                'description': _('Advanced analytics and customizable reporting capabilities.'),
                'features': [
                    _('Real-time dashboards and KPIs'),
                    _('Customizable report templates'),
                    _('Predictive analytics and forecasting'),
                    _('Compliance reporting automation'),
                    _('Data export and API integration')
                ],
                'color': '#f093fb'
            }
        ]
    }
    return render(request, 'normieapp/features.html', context)


# AJAX Validation Endpoints
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
    if len(username) < 3:
        return JsonResponse({
            'available': False,
            'message': _('Username must be at least 3 characters long.'),
            'type': 'error'
        })
    
    # Check maximum length
    if len(username) > 150:
        return JsonResponse({
            'available': False,
            'message': _('Username must be 150 characters or less.'),
            'type': 'error'
        })
    
    # Check if username exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'available': False,
            'message': _('This username is already taken.'),
            'type': 'error'
        })
    
    # Check for valid characters (alphanumeric, @, ., +, -, _)
    import re
    if not re.match(r'^[\w.@+-]+$', username):
        return JsonResponse({
            'available': False,
            'message': _('Username can only contain letters, numbers, and @/./+/-/_ characters.'),
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