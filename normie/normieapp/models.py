from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid

class UserProfile(models.Model):
    """Extended user profile with role-based permissions"""
    
    ROLE_CHOICES = [
        ('admin', _('Administrator')),
        ('manager', _('Manager')),
        ('chemscan_specialist', _('ChemScan Specialist')),
        ('environmental_reviewer', _('Environmental Reviewer')),
        ('manufacturing_reviewer', _('Manufacturing Reviewer')),
        ('standards_officer', _('Standards Officer')),
        ('read_only', _('Read Only')),
        ('applicant', _('Applicant')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='applicant')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Permission flags
    can_create_requests = models.BooleanField(default=True)
    can_edit_requests = models.BooleanField(default=True)
    can_delete_requests = models.BooleanField(default=False)
    can_approve_requests = models.BooleanField(default=False)
    can_perform_chemscan = models.BooleanField(default=False)
    can_environmental_review = models.BooleanField(default=False)
    can_manufacturing_review = models.BooleanField(default=False)
    can_standards_review = models.BooleanField(default=False)
    can_view_all_requests = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    can_view_audit_logs = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def save(self, *args, **kwargs):
        # Set permissions based on role
        if self.role == 'admin':
            self.can_create_requests = True
            self.can_edit_requests = True
            self.can_delete_requests = True
            self.can_approve_requests = True
            self.can_perform_chemscan = True
            self.can_environmental_review = True
            self.can_manufacturing_review = True
            self.can_standards_review = True
            self.can_view_all_requests = True
            self.can_manage_users = True
            self.can_view_reports = True
            self.can_view_audit_logs = True
        elif self.role == 'manager':
            self.can_create_requests = True
            self.can_edit_requests = True
            self.can_delete_requests = False
            self.can_approve_requests = True
            self.can_view_all_requests = True
            self.can_view_reports = True
            self.can_view_audit_logs = True
        elif self.role == 'chemscan_specialist':
            self.can_perform_chemscan = True
            self.can_view_all_requests = True
        elif self.role == 'environmental_reviewer':
            self.can_environmental_review = True
            self.can_view_all_requests = True
        elif self.role == 'manufacturing_reviewer':
            self.can_manufacturing_review = True
            self.can_view_all_requests = True
        elif self.role == 'standards_officer':
            self.can_standards_review = True
            self.can_approve_requests = True
            self.can_view_all_requests = True
        elif self.role == 'read_only':
            self.can_create_requests = False
            self.can_edit_requests = False
            self.can_delete_requests = False
            self.can_view_all_requests = True
        elif self.role == 'applicant':
            self.can_create_requests = True
            self.can_edit_requests = True
            self.can_delete_requests = False
            # Can only view own requests
            
        super().save(*args, **kwargs)

class ContactMessage(models.Model):
    """Contact form messages"""
    
    SUBJECT_CHOICES = [
        ('norms', _('Norms & Standards')),
        ('specs', _('Specifications')),
        ('chemicals', _('Chemical Standards')),
        ('materials', _('Material Testing')),
        ('archival', _('Archival Request')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('new', _('New')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    email = models.EmailField(verbose_name=_('Email'))
    department = models.CharField(max_length=100, blank=True, verbose_name=_('Department'))
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, verbose_name=_('Subject'))
    message = models.TextField(verbose_name=_('Message'))
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_contact_messages')
    flagged = models.BooleanField(default=False, help_text=_('Mark as important/flagged'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Internal notes
    internal_notes = models.TextField(blank=True, help_text=_('Internal notes for staff'))
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.created_at.strftime('%Y-%m-%d')})"
    
    @property
    def is_unread(self):
        """Check if message is unread (new status)"""
        return self.status == 'new'
    
    def mark_as_read(self):
        """Mark message as read by changing status from new to in_progress"""
        if self.status == 'new':
            self.status = 'in_progress'
            self.save()

class CMSRRequest(models.Model):
    """Main CMSR (Consumable Material Supply Request) model"""
    
    # Status choices
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('chemscan_pending', _('ChemScan Pending')),
        ('chemscan_completed', _('ChemScan Completed')),
        ('environmental_review', _('Environmental Review')),
        ('manufacturing_lab_review', _('Manufacturing Lab Review')),
        ('standards_office_review', _('Standards Office Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('requires_modification', _('Requires Modification')),
    ]
    
    # Classification choices
    NEED_CLASSIFICATION_CHOICES = [
        ('new', _('New Need')),
        ('change', _('Need Change')),
        ('replacement', _('Replacement')),
        ('extension', _('Extension')),
    ]
    
    PRODUCT_CLASSIFICATION_CHOICES = [
        ('substance', _('Substance')),
        ('part', _('Part')),
        ('mixture', _('Mixture')),
        ('article', _('Article')),
    ]
    
    # Basic Information (Fields 1-2)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_number = models.CharField(max_length=20, unique=True, blank=True)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cmsr_requests')
    applicant_name = models.CharField(max_length=100)
    application_date = models.DateField(auto_now_add=True)
    applicant_department = models.CharField(max_length=100)
    applicant_phone = models.CharField(max_length=20, blank=True)
    
    # Product Information (Fields 3-9)
    product_name = models.CharField(max_length=200, help_text=_("Unique designation from SDS"))
    foreign_part_number = models.CharField(max_length=100, blank=True)
    need_classification = models.CharField(max_length=20, choices=NEED_CLASSIFICATION_CHOICES)
    product_classification = models.CharField(max_length=20, choices=PRODUCT_CLASSIFICATION_CHOICES)
    reach_code = models.CharField(max_length=50, blank=True)
    supplier = models.CharField(max_length=200, help_text=_("Determined by purchasing"))
    manufacturer = models.CharField(max_length=200)
    
    # Usage Information (Fields 10-17)
    usage_purpose = models.TextField(help_text=_("Purpose, requirements, process description, application form"))
    engine_program = models.CharField(max_length=100, blank=True)
    location_site = models.CharField(max_length=200)
    area_team_leader = models.CharField(max_length=200, blank=True)
    product_relevant = models.BooleanField(help_text=_("Contact with aircraft parts?"))
    usage_duration = models.CharField(max_length=20, choices=[('short_term', _('Short-term')), ('long_term', _('Long-term'))])
    inventory_stock = models.BooleanField(default=False)
    sap_order = models.BooleanField(default=False)
    base_unit_sap = models.CharField(max_length=50, help_text=_("e.g., Gram, Liter, Piece"))
    monthly_demand = models.CharField(max_length=100)
    usage_frequency = models.CharField(max_length=100)
    quantity_per_application = models.CharField(max_length=100)
    
    # Documentation Requirements (Field 18)
    has_safety_datasheet = models.BooleanField(default=False)
    has_technical_datasheet = models.BooleanField(default=False)
    has_risk_assessment = models.BooleanField(default=False)
    has_product_approval = models.BooleanField(default=False)
    product_approval_specification = models.TextField(blank=True)
    
    # Additional Information (Fields 19-21)
    additional_explanations = models.TextField(blank=True)
    reference_past_applications = models.CharField(max_length=200, blank=True)
    desired_implementation_date = models.CharField(max_length=100, blank=True)
    
    # Status and Workflow
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Final Approval Information (Fields 51-52)
    final_part_number = models.CharField(max_length=50, blank=True)
    final_explanations = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('CMSR Request')
        verbose_name_plural = _('CMSR Requests')
    
    def __str__(self):
        return f"{self.application_number} - {self.product_name}"
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            # Generate application number: XXX/YYYY format
            year = self.application_date.year
            last_number = CMSRRequest.objects.filter(
                application_date__year=year
            ).count() + 1
            self.application_number = f"{last_number:03d}/{year}"
        super().save(*args, **kwargs)



# Below models are deprecated and will be removed in a future version.
# Please use the new implementations above instead.

class ChemScanAssessment(models.Model):
    """ChemScan assessment results (Fields 22-23)"""
    
    cmsr_request = models.OneToOneField(CMSRRequest, on_delete=models.CASCADE, related_name='chemscan')
    
    # ChemScan Information (Field 22)
    chemscan_performed_by_1 = models.CharField(max_length=100, blank=True)
    chemscan_date_1 = models.DateField(null=True, blank=True)
    chemscan_completed_1 = models.BooleanField(default=False)
    
    chemscan_performed_by_2 = models.CharField(max_length=100, blank=True)
    chemscan_date_2 = models.DateField(null=True, blank=True)
    chemscan_completed_2 = models.BooleanField(default=False)
    
    # Regulatory Classifications (Field 23a & 23b)
    # Component A
    chemvv_a = models.CharField(max_length=100, blank=True)
    other_a = models.CharField(max_length=100, blank=True)
    kmr_trgs905_a = models.BooleanField(default=False)
    arbmedvv_a = models.BooleanField(default=False)
    svhc_reach_xiv_a = models.BooleanField(default=False)
    chemvv_checkbox_a = models.BooleanField(default=False)
    agw_trgs900_a = models.BooleanField(default=False)
    odin_a = models.BooleanField(default=False)
    reach_xvii_a = models.BooleanField(default=False)
    other_checkbox_a = models.BooleanField(default=False)
    bgw_trgs903_a = models.BooleanField(default=False)
    erb_bek910_a = models.BooleanField(default=False)
    ex_protection_a = models.BooleanField(default=False)
    physical_danger_a = models.BooleanField(default=False)
    
    # Component B (similar fields)
    chemvv_b = models.CharField(max_length=100, blank=True)
    other_b = models.CharField(max_length=100, blank=True)
    kmr_trgs905_b = models.BooleanField(default=False)
    arbmedvv_b = models.BooleanField(default=False)
    svhc_b = models.BooleanField(default=False)
    chemvv_checkbox_b = models.BooleanField(default=False)
    agw_trgs900_b = models.BooleanField(default=False)
    odin_b = models.BooleanField(default=False)
    reach_xiv_b = models.BooleanField(default=False)
    other_checkbox_b = models.BooleanField(default=False)
    bgw_trgs903_b = models.BooleanField(default=False)
    erb_bek910_b = models.BooleanField(default=False)
    reach_xvii_b = models.BooleanField(default=False)
    physical_danger_b = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EnvironmentalAssessment(models.Model):
    """Environmental protection assessment (Fields 24-37)"""
    
    cmsr_request = models.OneToOneField(CMSRRequest, on_delete=models.CASCADE, related_name='environmental')
    
    # Water Protection (Fields 24-25)
    awsv_wgk_a = models.CharField(max_length=10, blank=True, help_text=_("Water hazard class"))
    awsv_wgk_b = models.CharField(max_length=10, blank=True)
    
    # Air Protection (Fields 26-27)
    air_protection_a = models.BooleanField(default=False)
    air_protection_b = models.BooleanField(default=False)
    
    # Waste Management (Fields 28-29)
    waste_key_a = models.CharField(max_length=20, blank=True)
    waste_key_b = models.CharField(max_length=20, blank=True)
    
    # VOC Assessment (Fields 30-31)
    voc_content_a = models.CharField(max_length=50, blank=True)
    voc_content_b = models.CharField(max_length=50, blank=True)
    
    # Additional Environmental Factors (Fields 32-37)
    environmental_measures = models.TextField(blank=True)
    disposal_instructions = models.TextField(blank=True)
    storage_requirements = models.TextField(blank=True)
    
    # Assessment Results
    environmental_approval = models.CharField(max_length=20, choices=[
        ('approved', _('Approved')),
        ('conditional', _('Conditional Approval')),
        ('rejected', _('Rejected'))
    ], blank=True)
    
    environmental_comments = models.TextField(blank=True)
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    assessment_date = models.DateField(null=True, blank=True)


class ManufacturingLabApproval(models.Model):
    """Manufacturing laboratory approval (Fields 40-49)"""
    
    cmsr_request = models.OneToOneField(CMSRRequest, on_delete=models.CASCADE, related_name='manufacturing_lab')
    
    # First Review (Fields 40-46)
    reviewer_name_1 = models.CharField(max_length=100, blank=True)
    review_date_1 = models.DateField(null=True, blank=True)
    
    shelf_life_requirement = models.CharField(max_length=20, choices=[
        ('not_relevant', _('Not Relevant')),
        ('min_days', _('Minimum Days')),
        ('other', _('Other'))
    ], blank=True)
    shelf_life_days = models.IntegerField(null=True, blank=True)
    
    certificate_requirement = models.CharField(max_length=20, choices=[
        ('not_required', _('Not Required')),
        ('2_1', _('2.1')),
        ('2_2', _('2.2')),
        ('3_1', _('3.1')),
        ('3_2', _('3.2')),
        ('other', _('Other'))
    ], blank=True)
    other_certificate = models.CharField(max_length=100, blank=True)
    
    mlc104_entry_required = models.CharField(max_length=20, choices=[
        ('not_required', _('Not Required')),
        ('required', _('Required')),
        ('update', _('Update Required'))
    ], blank=True)
    
    omat_entry_required = models.CharField(max_length=20, choices=[
        ('not_required', _('Not Required')),
        ('new', _('New Entry')),
        ('existing', _('Use Existing'))
    ], blank=True)
    omat_number = models.CharField(max_length=50, blank=True)
    
    product_approval_specification = models.TextField(blank=True)
    supplier_requirements = models.TextField(blank=True)
    
    # Second Review (Fields 47-49)
    reviewer_name_2 = models.CharField(max_length=100, blank=True)
    review_date_2 = models.DateField(null=True, blank=True)
    
    final_certificate_requirement = models.CharField(max_length=20, blank=True)
    final_other_certificate = models.CharField(max_length=100, blank=True)
    final_supplier_requirements = models.TextField(blank=True)


class StandardsOfficeApproval(models.Model):
    """Standards office final approval (Field 50)"""
    
    cmsr_request = models.OneToOneField(CMSRRequest, on_delete=models.CASCADE, related_name='standards_office')
    
    reviewer_name = models.CharField(max_length=100, blank=True)
    review_date = models.DateField(null=True, blank=True)
    
    final_approval = models.CharField(max_length=20, choices=[
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('conditional', _('Conditional Approval'))
    ], blank=True)
    
    final_comments = models.TextField(blank=True)


class CMSRDocument(models.Model):
    """Document attachments for CMSR requests"""
    
    DOCUMENT_TYPES = [
        ('safety_datasheet', _('Safety Datasheet (eSDB)')),
        ('technical_datasheet', _('Technical Datasheet')),
        ('risk_assessment', _('Risk Assessment')),
        ('product_approval', _('Product Approval')),
        ('specification', _('Specification')),
        ('certificate', _('Certificate')),
        ('other', _('Other'))
    ]
    
    cmsr_request = models.ForeignKey(CMSRRequest, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='cmsr_documents/%Y/%m/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']


class CMSRWorkflowLog(models.Model):
    """Audit trail for CMSR workflow changes"""
    
    cmsr_request = models.ForeignKey(CMSRRequest, on_delete=models.CASCADE, related_name='workflow_logs')
    previous_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    change_date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-change_date']
