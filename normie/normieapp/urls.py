"""
URL configuration for normieapp.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('incoming/', views.incoming, name='incoming'),	
    path('directory/', views.directory, name='directory'),
    path('chemscan/', views.chemscan, name='chemscan'),
    path('standards/', views.standards, name='standards'),
    path('requests/', views.requests, name='requests'),
    path('materials/', views.materials, name='materials'),
    path('releases/', views.releases, name='releases'),
    path('approvals/', views.approvals, name='approvals'),
    path('inventory/', views.inventory, name='inventory'),
    path('reports/', views.reports, name='reports'),
    path('audit/', views.audit, name='audit'),
    path('settings/', views.settings, name='settings'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    
    # CMSR (Consumable Material Supply Request) routes
    path('cmsr/', views.cmsr_list, name='cmsr_list'),
    path('cmsr/new/', views.cmsr_request, name='cmsr_request'),
    path('cmsr/<uuid:pk>/', views.cmsr_detail, name='cmsr_detail'),
    path('cmsr/<uuid:pk>/edit/', views.cmsr_edit, name='cmsr_edit'),
    
    # PDF Form handling routes
    path('pdf/upload/', views.pdf_upload, name='pdf_upload'),
    path('pdf/edit/<str:form_id>/', views.pdf_edit, name='pdf_edit'),
    path('pdf/save/<str:form_id>/', views.pdf_save, name='pdf_save'),
    path('pdf/download/<str:form_id>/', views.pdf_download, name='pdf_download'),
    path('pdf/debug/<str:form_id>/', views.pdf_debug, name='pdf_debug'),
] 