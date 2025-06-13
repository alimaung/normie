from django.shortcuts import render, redirect, get_object_or_404
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


@login_required
def notifications(request):
    """
    Notifications view.
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


@login_required(login_url='/admin/login/')
def cmsr_request(request):
    """
    CMSR (Consumable Material Supply Request) form view.
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
    return render(request, 'normieapp/cmsr_request.html', context)


@login_required
def cmsr_detail(request, pk):
    """
    CMSR request detail view with workflow management.
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
    return render(request, 'normieapp/cmsr_detail.html', context)


@login_required
def cmsr_list(request):
    """
    List view for CMSR requests with filtering and search.
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
    return render(request, 'normieapp/cmsr_list.html', context)


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


@login_required
def cmsr_edit(request, pk):
    """
    Edit CMSR request view.
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
    return render(request, 'normieapp/cmsr_edit.html', context)


@login_required
def cmsr_chemscan(request, pk):
    """
    ChemScan assessment view for CMSR request.
    """
    from .models import CMSRRequest, ChemScanAssessment
    from .forms import ChemScanAssessmentForm
    
    cmsr = get_object_or_404(CMSRRequest, pk=pk)
    
    # Check permissions - only ChemScan group can access
    if not request.user.groups.filter(name='ChemScan').exists() and not request.user.has_perm('normieapp.change_cmsrrequest'):
        messages.error(request, _('You do not have permission to perform ChemScan assessments.'))
        return redirect('cmsr_detail', pk=pk)
    
    # Get or create ChemScan assessment
    chemscan, created = ChemScanAssessment.objects.get_or_create(cmsr_request=cmsr)
    
    if request.method == 'POST':
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
        'chemscan': chemscan
    }
    return render(request, 'normieapp/cmsr_chemscan.html', context)


@login_required
def cmsr_environmental(request, pk):
    """
    Environmental assessment view for CMSR request.
    """
    from .models import CMSRRequest, EnvironmentalAssessment
    from .forms import EnvironmentalAssessmentForm
    
    cmsr = get_object_or_404(CMSRRequest, pk=pk)
    
    # Check permissions - only Environmental group can access
    if not request.user.groups.filter(name='Environmental').exists() and not request.user.has_perm('normieapp.change_cmsrrequest'):
        messages.error(request, _('You do not have permission to perform environmental assessments.'))
        return redirect('cmsr_detail', pk=pk)
    
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
    return render(request, 'normieapp/cmsr_environmental.html', context)


@login_required
def cmsr_manufacturing(request, pk):
    """
    Manufacturing lab approval view for CMSR request.
    """
    from .models import CMSRRequest, ManufacturingLabApproval
    from .forms import ManufacturingLabApprovalForm
    
    cmsr = get_object_or_404(CMSRRequest, pk=pk)
    
    # Check permissions - only Manufacturing Lab group can access
    if not request.user.groups.filter(name='Manufacturing Lab').exists() and not request.user.has_perm('normieapp.change_cmsrrequest'):
        messages.error(request, _('You do not have permission to perform manufacturing lab approvals.'))
        return redirect('cmsr_detail', pk=pk)
    
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
    return render(request, 'normieapp/cmsr_manufacturing.html', context)


@login_required
def cmsr_standards(request, pk):
    """
    Standards office approval view for CMSR request.
    """
    from .models import CMSRRequest, StandardsOfficeApproval
    from .forms import StandardsOfficeApprovalForm
    
    cmsr = get_object_or_404(CMSRRequest, pk=pk)
    
    # Check permissions - only Standards Office group can access
    if not request.user.groups.filter(name='Standards Office').exists() and not request.user.has_perm('normieapp.change_cmsrrequest'):
        messages.error(request, _('You do not have permission to perform standards office approvals.'))
        return redirect('cmsr_detail', pk=pk)
    
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
    return render(request, 'normieapp/cmsr_standards.html', context)


@login_required
def cmsr_documents(request, pk):
    """
    Document management view for CMSR request.
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
    return render(request, 'normieapp/cmsr_documents.html', context) 