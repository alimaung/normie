"""
URL configuration for normieapp.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
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
    path('cmsr/<uuid:pk>/chemscan/', views.cmsr_chemscan, name='cmsr_chemscan'),
    path('cmsr/<uuid:pk>/environmental/', views.cmsr_environmental, name='cmsr_environmental'),
    path('cmsr/<uuid:pk>/manufacturing/', views.cmsr_manufacturing, name='cmsr_manufacturing'),
    path('cmsr/<uuid:pk>/standards/', views.cmsr_standards, name='cmsr_standards'),
    path('cmsr/<uuid:pk>/documents/', views.cmsr_documents, name='cmsr_documents'),
] 