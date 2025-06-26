from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import (
    CMSRRequest, ChemScanAssessment, EnvironmentalAssessment, 
    ManufacturingLabApproval, StandardsOfficeApproval, CMSRDocument, UserProfile
)


class SignUpForm(UserCreationForm):
    """Custom signup form with additional fields"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('First name')
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Last name')
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email address')
        })
    )
    
    # Removed department and phone fields - no longer needed

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Choose a username')
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update password field widgets
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Create a strong password')
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Confirm your password')
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # The signal will automatically create a UserProfile, so we get or create it
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
            
            # Update the profile with our form data
            profile.role = 'read_only'
            # Department and phone are no longer collected during signup
            profile.save()
        return user


class CMSRRequestForm(forms.ModelForm):
    """Main CMSR request form with all required fields"""
    
    class Meta:
        model = CMSRRequest
        fields = [
            'application_number', 'applicant_department', 'applicant_phone',
            'product_name', 'foreign_part_number', 'need_classification', 
            'product_classification', 'reach_code', 'supplier', 'manufacturer',
            'usage_purpose', 'engine_program', 'location_site', 'area_team_leader',
            'product_relevant', 'usage_duration', 'inventory_stock', 'sap_order',
            'base_unit_sap', 'monthly_demand', 'usage_frequency', 'quantity_per_application',
            'has_safety_datasheet', 'has_technical_datasheet', 'has_risk_assessment',
            'has_product_approval', 'product_approval_specification',
            'additional_explanations', 'reference_past_applications', 'desired_implementation_date'
        ]
        
        widgets = {
            'application_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Auto-generated if left empty'),
                'readonly': True
            }),
            'applicant_department': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'applicant_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel'
            }),
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': _('Unique designation from SDS')
            }),
            'foreign_part_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'need_classification': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'product_classification': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'reach_code': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'supplier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Determined by purchasing')
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'usage_purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'required': True,
                'placeholder': _('Purpose, requirements, process description, application form')
            }),
            'engine_program': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'location_site': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'area_team_leader': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'product_relevant': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'usage_duration': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'inventory_stock': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sap_order': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'base_unit_sap': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., Gram, Liter, Piece')
            }),
            'monthly_demand': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'usage_frequency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., daily, weekly, monthly')
            }),
            'quantity_per_application': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'has_safety_datasheet': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_technical_datasheet': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_risk_assessment': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'has_product_approval': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'product_approval_specification': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'additional_explanations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Additional information (MSRR, CSS, OMat, etc.)')
            }),
            'reference_past_applications': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., 005/2020, 234/2022')
            }),
            'desired_implementation_date': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g., immediately, Q2 2024')
            })
        }
        
        labels = {
            'application_number': _('Application Number'),
            'applicant_department': _('Department'),
            'applicant_phone': _('Phone Number'),
            'product_name': _('Product Name/Designation'),
            'foreign_part_number': _('Foreign Part Number'),
            'need_classification': _('Need Classification'),
            'product_classification': _('Product Classification'),
            'reach_code': _('REACh Code'),
            'supplier': _('Supplier'),
            'manufacturer': _('Manufacturer'),
            'usage_purpose': _('Usage Purpose & Process Description'),
            'engine_program': _('Engine Program'),
            'location_site': _('Location/Site'),
            'area_team_leader': _('Area Team Leader'),
            'product_relevant': _('Product Relevant (Contact with aircraft parts?)'),
            'usage_duration': _('Usage Duration'),
            'inventory_stock': _('Inventory Stock?'),
            'sap_order': _('Order via SAP?'),
            'base_unit_sap': _('Base Unit SAP'),
            'monthly_demand': _('Monthly Demand'),
            'usage_frequency': _('Usage Frequency'),
            'quantity_per_application': _('Quantity per Application'),
            'has_safety_datasheet': _('Safety Datasheet (eSDB)'),
            'has_technical_datasheet': _('Technical Datasheet'),
            'has_risk_assessment': _('Risk Assessment'),
            'has_product_approval': _('Product Approval'),
            'product_approval_specification': _('Product Approval Specification'),
            'additional_explanations': _('Additional Explanations'),
            'reference_past_applications': _('Reference to Past Applications'),
            'desired_implementation_date': _('Desired Implementation Date')
        }


class ChemScanAssessmentForm(forms.ModelForm):
    """ChemScan assessment form for regulatory compliance"""
    
    class Meta:
        model = ChemScanAssessment
        exclude = ['cmsr_request', 'created_at', 'updated_at']
        
        widgets = {
            'chemscan_performed_by_1': forms.TextInput(attrs={'class': 'form-control'}),
            'chemscan_date_1': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'chemscan_completed_1': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'chemscan_performed_by_2': forms.TextInput(attrs={'class': 'form-control'}),
            'chemscan_date_2': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'chemscan_completed_2': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'chemvv_a': forms.TextInput(attrs={'class': 'form-control'}),
            'other_a': forms.TextInput(attrs={'class': 'form-control'}),
            'chemvv_b': forms.TextInput(attrs={'class': 'form-control'}),
            'other_b': forms.TextInput(attrs={'class': 'form-control'}),
        }


class EnvironmentalAssessmentForm(forms.ModelForm):
    """Environmental protection assessment form"""
    
    class Meta:
        model = EnvironmentalAssessment
        exclude = ['cmsr_request']
        
        widgets = {
            'awsv_wgk_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Water hazard class')}),
            'awsv_wgk_b': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Water hazard class')}),
            'air_protection_a': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'air_protection_b': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'waste_key_a': forms.TextInput(attrs={'class': 'form-control'}),
            'waste_key_b': forms.TextInput(attrs={'class': 'form-control'}),
            'voc_content_a': forms.TextInput(attrs={'class': 'form-control'}),
            'voc_content_b': forms.TextInput(attrs={'class': 'form-control'}),
            'environmental_measures': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'disposal_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'storage_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'environmental_approval': forms.Select(attrs={'class': 'form-control'}),
            'environmental_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assessment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }


class ManufacturingLabApprovalForm(forms.ModelForm):
    """Manufacturing laboratory approval form"""
    
    class Meta:
        model = ManufacturingLabApproval
        exclude = ['cmsr_request']
        
        widgets = {
            'reviewer_name_1': forms.TextInput(attrs={'class': 'form-control'}),
            'review_date_1': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shelf_life_requirement': forms.Select(attrs={'class': 'form-control'}),
            'shelf_life_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'certificate_requirement': forms.Select(attrs={'class': 'form-control'}),
            'other_certificate': forms.TextInput(attrs={'class': 'form-control'}),
            'mlc104_entry_required': forms.Select(attrs={'class': 'form-control'}),
            'omat_entry_required': forms.Select(attrs={'class': 'form-control'}),
            'omat_number': forms.TextInput(attrs={'class': 'form-control'}),
            'product_approval_specification': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supplier_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reviewer_name_2': forms.TextInput(attrs={'class': 'form-control'}),
            'review_date_2': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'final_certificate_requirement': forms.TextInput(attrs={'class': 'form-control'}),
            'final_other_certificate': forms.TextInput(attrs={'class': 'form-control'}),
            'final_supplier_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }


class StandardsOfficeApprovalForm(forms.ModelForm):
    """Standards office final approval form"""
    
    class Meta:
        model = StandardsOfficeApproval
        exclude = ['cmsr_request']
        
        widgets = {
            'reviewer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'final_approval': forms.Select(attrs={'class': 'form-control'}),
            'final_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }


class CMSRDocumentForm(forms.ModelForm):
    """Document upload form for CMSR requests"""
    
    class Meta:
        model = CMSRDocument
        fields = ['document_type', 'file', 'description']
        
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.xls,.xlsx'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
        }


class CMSRSearchForm(forms.Form):
    """Search and filter form for CMSR requests"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search by application number, product name, manufacturer...')
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', _('All Statuses'))] + CMSRRequest.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    my_requests = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    ) 