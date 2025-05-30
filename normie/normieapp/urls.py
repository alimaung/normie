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
] 