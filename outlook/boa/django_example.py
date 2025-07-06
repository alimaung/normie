"""
Django Integration Example for Contact Search

This file shows how to integrate the contact search functionality
into Django views and API endpoints.
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

# Import the search service functions
from search_contacts import (
    search_contacts_service, 
    get_contact_by_email_service, 
    get_contact_statistics_service
)


class ContactSearchView(View):
    """Django view for contact search functionality"""
    
    def get(self, request):
        """Handle GET requests for contact search"""
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        fuzzy = request.GET.get('fuzzy', 'true').lower() == 'true'
        
        if not query:
            return JsonResponse({
                'error': 'Query parameter "q" is required',
                'results': []
            }, status=400)
        
        try:
            results = search_contacts_service(query, limit=limit, fuzzy=fuzzy)
            
            # Remove internal relevance score for API response
            clean_results = []
            for contact in results:
                clean_contact = {k: v for k, v in contact.items() if k != '_relevance_score'}
                clean_results.append(clean_contact)
            
            return JsonResponse({
                'query': query,
                'count': len(clean_results),
                'results': clean_results
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Search failed: {str(e)}',
                'results': []
            }, status=500)


class ContactDetailView(View):
    """Django view for getting contact by email"""
    
    def get(self, request, email):
        """Get contact details by email address"""
        try:
            contact = get_contact_by_email_service(email)
            
            if contact:
                # Remove internal fields
                clean_contact = {k: v for k, v in contact.items() if k != '_relevance_score'}
                return JsonResponse({
                    'found': True,
                    'contact': clean_contact
                })
            else:
                return JsonResponse({
                    'found': False,
                    'message': f'No contact found for email: {email}'
                }, status=404)
                
        except Exception as e:
            return JsonResponse({
                'error': f'Lookup failed: {str(e)}'
            }, status=500)


class ContactStatsView(View):
    """Django view for contact database statistics"""
    
    def get(self, request):
        """Get contact database statistics"""
        try:
            stats = get_contact_statistics_service()
            return JsonResponse(stats)
            
        except Exception as e:
            return JsonResponse({
                'error': f'Stats retrieval failed: {str(e)}'
            }, status=500)


# Template-based views for web interface
def contact_search_page(request):
    """Render the contact search page"""
    return render(request, 'contacts/search.html')


def contact_search_results(request):
    """Handle search form submission and display results"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))
    
    if not query:
        return render(request, 'contacts/search.html', {
            'error': 'Please enter a search query'
        })
    
    try:
        results = search_contacts_service(query, limit=limit)
        
        return render(request, 'contacts/results.html', {
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return render(request, 'contacts/search.html', {
            'error': f'Search failed: {str(e)}'
        })


# URL patterns (add these to your urls.py)
"""
from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/contacts/search/', views.ContactSearchView.as_view(), name='contact_search_api'),
    path('api/contacts/email/<str:email>/', views.ContactDetailView.as_view(), name='contact_detail_api'),
    path('api/contacts/stats/', views.ContactStatsView.as_view(), name='contact_stats_api'),
    
    # Web interface
    path('contacts/', views.contact_search_page, name='contact_search'),
    path('contacts/results/', views.contact_search_results, name='contact_results'),
]
"""

# Example HTML templates
SEARCH_TEMPLATE = """
<!-- contacts/search.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Contact Search</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .search-box { margin: 20px 0; }
        .search-box input[type="text"] { width: 300px; padding: 10px; }
        .search-box button { padding: 10px 20px; }
        .error { color: red; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Contact Search</h1>
    
    {% if error %}
        <div class="error">{{ error }}</div>
    {% endif %}
    
    <form method="GET" action="{% url 'contact_results' %}">
        <div class="search-box">
            <input type="text" name="q" placeholder="Search contacts..." value="{{ request.GET.q }}">
            <input type="number" name="limit" placeholder="Limit" value="{{ request.GET.limit|default:10 }}" min="1" max="50">
            <button type="submit">Search</button>
        </div>
    </form>
    
    <h3>Search Examples:</h3>
    <ul>
        <li>Search by name: "John Smith"</li>
        <li>Search by email: "john.smith@company.com"</li>
        <li>Search by department: "IT Development"</li>
        <li>Search by title: "Manager"</li>
    </ul>
</body>
</html>
"""

RESULTS_TEMPLATE = """
<!-- contacts/results.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .result { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .name { font-weight: bold; font-size: 18px; }
        .email { color: #0066cc; }
        .detail { margin: 5px 0; }
        .back-link { margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Search Results</h1>
    
    <div class="back-link">
        <a href="{% url 'contact_search' %}">← Back to Search</a>
    </div>
    
    <p>Found {{ count }} contacts for "{{ query }}"</p>
    
    {% for contact in results %}
        <div class="result">
            <div class="name">{{ contact.DisplayName|default:"Unknown" }}</div>
            {% if contact.SmtpAddress %}
                <div class="email">{{ contact.SmtpAddress }}</div>
            {% endif %}
            {% if contact.Title %}
                <div class="detail"><strong>Title:</strong> {{ contact.Title }}</div>
            {% endif %}
            {% if contact.CompanyName %}
                <div class="detail"><strong>Company:</strong> {{ contact.CompanyName }}</div>
            {% endif %}
            {% if contact.DepartmentName %}
                <div class="detail"><strong>Department:</strong> {{ contact.DepartmentName }}</div>
            {% endif %}
            {% if contact.BusinessTelephoneNumber %}
                <div class="detail"><strong>Phone:</strong> {{ contact.BusinessTelephoneNumber }}</div>
            {% endif %}
            {% if contact.OfficeLocation %}
                <div class="detail"><strong>Office:</strong> {{ contact.OfficeLocation }}</div>
            {% endif %}
        </div>
    {% empty %}
        <p>No contacts found.</p>
    {% endfor %}
</body>
</html>
"""

# Example usage in Django management command
"""
# management/commands/search_contacts.py
from django.core.management.base import BaseCommand
from myapp.views import search_contacts_service

class Command(BaseCommand):
    help = 'Search contacts from command line'
    
    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='Search query')
        parser.add_argument('--limit', type=int, default=10, help='Limit results')
    
    def handle(self, *args, **options):
        query = options['query']
        limit = options['limit']
        
        results = search_contacts_service(query, limit=limit)
        
        self.stdout.write(f"Found {len(results)} contacts for '{query}':")
        for contact in results:
            name = contact.get('DisplayName', 'Unknown')
            email = contact.get('SmtpAddress', 'No email')
            self.stdout.write(f"  - {name} ({email})")
""" 