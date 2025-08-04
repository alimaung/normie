from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, CMSRRequest, ChemScanAssessment, EnvironmentalAssessment,
    ManufacturingLabApproval, StandardsOfficeApproval, CMSRDocument, CMSRWorkflowLog,
    ContactMessage
)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_select_related = ('profile',)

    def get_role(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.get_role_display()
        return 'No Profile'
    get_role.short_description = 'Role'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'created_at')
    list_filter = ('role', 'department', 'created_at')
    search_fields = ('user__username', 'user__email', 'department')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'role', 'department', 'phone')
        }),
        ('Permissions', {
            'fields': (
                'can_create_requests', 'can_edit_requests', 'can_delete_requests',
                'can_approve_requests', 'can_perform_chemscan', 'can_environmental_review',
                'can_manufacturing_review', 'can_standards_review', 'can_view_all_requests',
                'can_manage_users', 'can_view_reports', 'can_view_audit_logs'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CMSRRequest)
class CMSRRequestAdmin(admin.ModelAdmin):
    list_display = ('application_number', 'product_name', 'applicant', 'status', 'application_date')
    list_filter = ('status', 'need_classification', 'product_classification', 'application_date')
    search_fields = ('application_number', 'product_name', 'applicant__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('application_number', 'applicant', 'applicant_name', 'applicant_department', 'applicant_phone')
        }),
        ('Product Information', {
            'fields': ('product_name', 'foreign_part_number', 'need_classification', 'product_classification', 'reach_code', 'supplier', 'manufacturer')
        }),
        ('Usage Information', {
            'fields': ('usage_purpose', 'engine_program', 'location_site', 'area_team_leader', 'product_relevant', 'usage_duration', 'inventory_stock', 'sap_order', 'base_unit_sap', 'monthly_demand', 'usage_frequency', 'quantity_per_application')
        }),
        ('Documentation', {
            'fields': ('has_safety_datasheet', 'has_technical_datasheet', 'has_risk_assessment', 'has_product_approval', 'product_approval_specification')
        }),
        ('Additional Information', {
            'fields': ('additional_explanations', 'reference_past_applications', 'desired_implementation_date')
        }),
        ('Status and Final Approval', {
            'fields': ('status', 'final_part_number', 'final_explanations')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models
admin.site.register(ChemScanAssessment)
admin.site.register(EnvironmentalAssessment)
admin.site.register(ManufacturingLabApproval)
admin.site.register(StandardsOfficeApproval)
admin.site.register(CMSRDocument)
admin.site.register(CMSRWorkflowLog)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'subject', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'department')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'assigned_to', 'internal_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
