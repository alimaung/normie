"""
URL configuration for normieapp.
"""

from django.urls import path
from . import views
from .views.auth import settings as auth_settings
from .views.contact import contact_view, contact_messages_inbox, contact_message_action, contact_messages_archived

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
    
    # MLC Check routes
    path('mlc-check/', views.mlc_check, name='mlc_check'),
    path('mlc-check/search/', views.mlc_search, name='mlc_search'),
    path('mlc-check/process-sds/', views.mlc_process_sds, name='mlc_upload_sds'),
    path('mlc-check/info/', views.mlc_database_info, name='mlc_database_info'),
    
    # Email inbox routes
    path('inbox/', views.inbox, name='inbox'),
    
    # Folder-specific routes
    path('inbox/folder/<str:folder_name>/', views.inbox_folder, name='inbox_folder'),
    path('inbox/sent/', views.inbox_sent, name='inbox_sent'),
    path('inbox/deleted/', views.inbox_deleted, name='inbox_deleted'), 
    path('inbox/drafts/', views.inbox_drafts, name='inbox_drafts'),
    path('inbox/outbox/', views.inbox_outbox, name='inbox_outbox'),
    
    # Email actions
    path('inbox/view/<str:message_id>/', views.inbox_view_message, name='inbox_view_message'),
    path('inbox/compose/', views.inbox_compose, name='inbox_compose'),
    path('inbox/reply/<str:message_id>/', views.inbox_reply, name='inbox_reply'),
    path('inbox/send/', views.inbox_send_email, name='inbox_send_email'),
    path('inbox/search/', views.inbox_search, name='inbox_search'),
    path('inbox/refresh/', views.inbox_refresh, name='inbox_refresh'),
    path('inbox/status/', views.inbox_status, name='inbox_status'),
    
    # Read/Unread functionality
    path('inbox/mark-read-unread/', views.inbox_mark_read_unread, name='inbox_mark_read_unread'),
    path('inbox/mark-read-unread/<str:message_id>/', views.inbox_mark_single_read_unread, name='inbox_mark_single_read_unread'),
    
    # Debug and utilities
    path('inbox/test-accounts/', views.inbox_test_accounts, name='inbox_test_accounts'),
    path('inbox/debug/<str:message_id>/', views.inbox_debug_email, name='inbox_debug_email'),
    path('inbox/attachment/<str:message_id>/<str:filename>/', views.inbox_get_attachment, name='inbox_get_attachment'),
    
    # Legacy routes (maintain compatibility)
    path('inbox/delete/<str:message_id>/', views.inbox_delete_message, name='inbox_delete_message'),
    path('inbox/mark-read/<str:message_id>/', views.inbox_mark_message_read, name='inbox_mark_message_read'),
    path('inbox/categorize/<str:message_id>/', views.inbox_categorize_message, name='inbox_categorize_message'),
    path('inbox/delete/', views.inbox_delete, name='inbox_delete'),
    path('inbox/categorize/', views.inbox_categorize, name='inbox_categorize'),
    path('inbox/mark-read/', views.inbox_mark_read, name='inbox_mark_read'),
    
    # Flag functionality
    path('inbox/flag/', views.inbox_flag_email, name='inbox_flag_email'),
    path('inbox/flag/<str:message_id>/', views.inbox_flag_single_email, name='inbox_flag_single_email'),
    
    # Contact autocomplete functionality
    path('inbox/contacts/autocomplete/', views.inbox_contact_autocomplete, name='inbox_contact_autocomplete'),
    path('inbox/contacts/stats/', views.inbox_contact_stats, name='inbox_contact_stats'),
    
    # Contact management pages
    path('contacts/', views.contacts_page, name='contacts'),
    path('contacts/search/', views.contacts_search, name='contacts_search'),
    path('contacts/detail/<str:email>/', views.contact_detail, name='contact_detail'),
    path('contacts/export/', views.contacts_export, name='contacts_export'),
    path('contacts/stats/', views.contacts_stats, name='contacts_stats'),
    
    # Public pages for guests
    path('about/', views.about, name='about'),
    path('contact/', contact_view, name='contact'),
    path('features/', views.features_detail, name='features_detail'),
    
    # Contact messages (inbox integration)
    path('inbox/contact/', contact_messages_inbox, name='inbox_contact'),
    path('inbox/contact/action/', contact_message_action, name='contact_message_action'),
    path('inbox/contact/archived/', contact_messages_archived, name='contact_messages_archived'),
    
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
    
    # DIN Standards routes
    path('din/', views.din_search, name='din_search'),
    path('din/search/', views.din_search_api, name='din_search_api'),
    path('din/order/', views.din_order, name='din_order'),
    
    # Under construction page
    path('under-construction/', views.under_construction, name='under_construction'),
] 