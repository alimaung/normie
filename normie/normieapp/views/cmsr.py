from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Q
from ..decorators import (
    restrict_read_only_users, role_required,
    user_can_access_request
)
from .utils import get_next_possible_statuses


@restrict_read_only_users
def cmsr_request(request):
    """
    CMSR (Consumable Material Supply Request) form view - requires applicant role or above.
    Handles the complete multi-step approval workflow.
    """
    from ..models import CMSRRequest, CMSRDocument
    from ..forms import CMSRRequestForm, CMSRDocumentForm
    
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
    from ..models import CMSRRequest, CMSRWorkflowLog
    
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
    from ..models import CMSRRequest
    from django.core.paginator import Paginator
    
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


@restrict_read_only_users
def cmsr_edit(request, pk):
    """
    Edit CMSR request view - requires applicant role or above.
    """
    from ..models import CMSRRequest
    from ..forms import CMSRRequestForm
    
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


@restrict_read_only_users
def cmsr_documents(request, pk):
    """
    Document management view for CMSR request - requires applicant role or above.
    """
    from ..models import CMSRRequest, CMSRDocument
    from ..forms import CMSRDocumentForm
    
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


@role_required('admin', 'manager', 'chemscan_specialist')
def cmsr_chemscan(request, pk):
    """
    ChemScan assessment view for CMSR request - restricted to ChemScan specialists, managers, and admins.
    """
    from ..models import CMSRRequest, ChemScanAssessment
    from ..forms import ChemScanAssessmentForm
    
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
    from ..models import CMSRRequest, EnvironmentalAssessment
    from ..forms import EnvironmentalAssessmentForm
    
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
    from ..models import CMSRRequest, ManufacturingLabApproval
    from ..forms import ManufacturingLabApprovalForm
    
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
    from ..models import CMSRRequest, StandardsOfficeApproval
    from ..forms import StandardsOfficeApprovalForm
    
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