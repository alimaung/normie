"""
URL configuration for normieapp.
"""

from django.urls import path
from . import views
from .views.auth import settings as auth_settings

urlpatterns = [
    path('', views.home, name='home'),
    path('requests/', views.requests_page, name='requests'),	
    path('directory/', views.directory, name='directory'),
    path('directory/row/<int:row_number>/', views.directory_detail, name='directory_detail'),
    path('tkz/', views.tkz, name='tkz'),
    path('tkz/part/<int:row_number>/', views.tkz_detail, name='tkz_detail'),
    path('chemscan/', views.chemscan, name='chemscan'),
    path('standards/', views.standards, name='standards'),
    path('requests/', views.requests, name='requests'),
    path('materials/', views.materials, name='materials'),
    path('releases/', views.releases, name='releases'),
    path('approvals/', views.approvals, name='approvals'),
    path('inventory/', views.inventory, name='inventory'),
    path('reports/', views.reports, name='reports'),
    path('audit/', views.audit, name='audit'),
    path('settings/', auth_settings, name='settings'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    
    # Open request - accessible to all users
    path('open-request/', views.open_request, name='open_request'),
    
    # Email inbox routes
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/view/<str:message_id>/', views.inbox_view_message, name='inbox_view_message'),
    path('inbox/compose/', views.inbox_compose, name='inbox_compose'),
    path('inbox/reply/<str:message_id>/', views.inbox_reply, name='inbox_reply'),
    path('inbox/forward/<str:message_id>/', views.inbox_forward, name='inbox_forward'),
    path('inbox/delete/<str:message_id>/', views.inbox_delete_message, name='inbox_delete_message'),
    path('inbox/categorize/<str:message_id>/', views.inbox_categorize_message, name='inbox_categorize_message'),
    path('inbox/delete/', views.inbox_delete, name='inbox_delete'),
    path('inbox/categorize/', views.inbox_categorize, name='inbox_categorize'),
    
    # Public pages for guests
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('features/', views.features_detail, name='features_detail'),
    
    # User management routes
    path('users/', views.user_management, name='user_management'),
    path('my-profile/', views.user_profile_view, name='user_profile'),
    
    # CMSR (Consumable Material Supply Request) routes
    path('cmsr/', views.cmsr_list, name='cmsr_list'),
    path('cmsr/new/', views.cmsr_request, name='cmsr_request'),
    path('cmsr/<uuid:pk>/', views.cmsr_detail, name='cmsr_detail'),
    path('cmsr/<uuid:pk>/edit/', views.cmsr_edit, name='cmsr_edit'),
    path('cmsr/<uuid:pk>/chemscan/', views.cmsr_chemscan, name='cmsr_chemscan'),
    path('cmsr/<uuid:pk>/environmental/', views.cmsr_environmental, name='cmsr_environmental'),
    path('cmsr/<uuid:pk>/manufacturing/', views.cmsr_manufacturing, name='cmsr_manufacturing'),
    path('cmsr/<uuid:pk>/standards/', views.cmsr_standards, name='cmsr_standards'),
    path('cmsr/<uuid:pk>/documents/', views.cmsr_documents, name='cmsr_documents'),
    
    # PDF Parser routes
    path('pdf-parser/', views.pdf_parser, name='pdf_parser'),
    path('pdf-parser/upload/', views.pdf_upload, name='pdf_upload'),
    path('pdf-parser/editor/<str:form_id>/', views.pdf_editor, name='pdf_editor'),
    path('pdf-parser/save/<str:form_id>/', views.pdf_save, name='pdf_save'),
    path('pdf-parser/download/<str:form_id>/', views.pdf_download, name='pdf_download'),
    path('pdf-parser/debug/<str:form_id>/', views.pdf_debug, name='pdf_debug'),
    
    # PDF Form routes (alternative access path)
    path('pdf_form/pdf_form/', views.pdf_parser, name='pdf_form_alt'),
    
    # Applicant State Parser routes
    path('applicant-state-parser/', views.applicant_state_parser, name='applicant_state_parser'),
    path('applicant-state-parser/upload/', views.applicant_upload, name='applicant_upload'),
    path('applicant-state-parser/editor/<str:form_id>/', views.applicant_editor, name='applicant_editor'),
    path('applicant-state-parser/save/<str:form_id>/', views.applicant_save, name='applicant_save'),
    path('applicant-state-parser/download/<str:form_id>/', views.applicant_download, name='applicant_download'),
    
    # AJAX validation endpoints
    path('ajax/check-username/', views.check_username_availability, name='check_username'),
    path('ajax/check-email/', views.check_email_availability, name='check_email'),
    
    # Mock template routes
    path('solutions_norm/', views.solutions_norm, name='solutions_norm'),
    path('solutions_chemicals/', views.solutions_chemicals, name='solutions_chemicals'),
    path('solutions_spec/', views.solutions_spec, name='solutions_spec'),
    path('solutions_directory/', views.solutions_directory, name='solutions_directory'),
    path('solutions_tkz/', views.solutions_tkz, name='solutions_tkz'),
    
    # Under construction page
    path('under-construction/', views.under_construction, name='under_construction'),
    ] 