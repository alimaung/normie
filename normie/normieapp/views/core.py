from django.shortcuts import render
from django.utils.translation import gettext as _


def home(request):
    """
    Home page view for the Normie standards and material management system.
    """
    return render(request, 'normieapp/home.html')


def about(request):
    """
    About page - public access for guests.
    """
    context = {
        'page_title': _('About Normie'),
        'team_members': [
            {
                'name': 'Dr. Sarah Chen',
                'role': 'Chief Technology Officer',
                'description': 'Expert in standards management with 15+ years experience',
                'image_color': '#667eea'
            },
            {
                'name': 'Michael Rodriguez',
                'role': 'Head of Product',
                'description': 'Specializes in workflow optimization and user experience',
                'image_color': '#764ba2'
            },
            {
                'name': 'Anna Schmidt',
                'role': 'Compliance Director',
                'description': 'Regulatory compliance and quality assurance specialist',
                'image_color': '#f093fb'
            },
        ],
        'stats': {
            'years_experience': 12,
            'clients_served': 500,
            'standards_managed': 10000,
            'countries': 25
        }
    }
    return render(request, 'normieapp/about.html', context)


def contact(request):
    """
    Contact page - public access for guests.
    """
    from django.shortcuts import redirect
    from django.contrib import messages
    
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you would typically send an email or save to database
        # For now, just show a success message
        messages.success(request, _('Thank you for your message! We will get back to you soon.'))
        return redirect('contact')
    
    context = {
        'page_title': _('Contact Us'),
        'office_locations': [
            {
                'city': 'Munich',
                'country': 'Germany',
                'address': 'Maximilianstraße 35, 80539 München',
                'phone': '+49 89 123 456 789',
                'email': 'munich@normie.de'
            },
            {
                'city': 'Frankfurt',
                'country': 'Germany', 
                'address': 'Zeil 106, 60313 Frankfurt am Main',
                'phone': '+49 69 987 654 321',
                'email': 'frankfurt@normie.de'
            }
        ]
    }
    return render(request, 'normieapp/contact.html', context)


def features_detail(request):
    """
    Detailed features page - public access for guests.
    """
    context = {
        'page_title': _('Features & Capabilities'),
        'feature_categories': [
            {
                'title': _('Standards Management'),
                'description': _('Comprehensive tools for creating, maintaining, and tracking organizational standards.'),
                'features': [
                    _('Version control and history tracking'),
                    _('Collaborative editing and review workflows'),
                    _('Automated compliance checking'),
                    _('Document templates and standardization'),
                    _('Integration with regulatory databases')
                ],
                'color': '#667eea'
            },
            {
                'title': _('Request Processing'),
                'description': _('Streamlined material request workflows with intelligent automation.'),
                'features': [
                    _('Smart form validation and auto-completion'),
                    _('Role-based approval routing'),
                    _('Real-time status tracking'),
                    _('Automated notifications and reminders'),
                    _('Integration with procurement systems')
                ],
                'color': '#764ba2'
            },
            {
                'title': _('Analytics & Reporting'),
                'description': _('Advanced analytics and customizable reporting capabilities.'),
                'features': [
                    _('Real-time dashboards and KPIs'),
                    _('Customizable report templates'),
                    _('Predictive analytics and forecasting'),
                    _('Compliance reporting automation'),
                    _('Data export and API integration')
                ],
                'color': '#f093fb'
            }
        ]
    }
    return render(request, 'normieapp/features.html', context)


def solutions_norm(request):
    return render(request, 'normieapp/solutions_norm.html')


def solutions_chemicals(request):
    return render(request, 'normieapp/solutions_chemicals.html')


def solutions_spec(request):
    return render(request, 'normieapp/solutions_spec.html')


def solutions_directory(request):
    return render(request, 'normieapp/solutions_directory.html')


def solutions_tkz(request):
    return render(request, 'normieapp/solutions_tkz.html')


def under_construction(request):
    """
    Under construction page view - public access.
    """
    return render(request, 'normieapp/under_contruction.html')


def open_request(request):
    """
    Open Request page view - public access for all users including guests.
    Handles both GET (display form) and POST (submit form) requests.
    """
    from django.http import JsonResponse
    from django.utils.translation import gettext as _
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = [
                'field_2a', 'field_2b', 'field_2c', 'field_2d', 'field_3',
                'field_5', 'field_6', 'field_7', 'field_8', 'field_9',
                'field_10', 'field_11', 'field_12a', 'field_12b', 'field_14'
            ]
            
            missing_fields = []
            for field in required_fields:
                if not data.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'message': f'Required fields missing: {", ".join(missing_fields)}'
                })
            
            # Generate Antragnummer (XXX/YYYY format)
            from datetime import datetime
            current_year = datetime.now().year
            
            # For now, we'll simulate auto-increment logic
            # In a real implementation, this would query the database for the next number
            next_number = 1  # This would be calculated from database
            antragnummer = f"{next_number:03d}/{current_year}"
            
            # Print form data to console
            print("\n" + "="*80)
            print("NEW OPEN REQUEST SUBMITTED")
            print("="*80)
            print(f"Antragnummer: {antragnummer}")
            print(f"TKZ: {data.get('tkz', 'Auto-generated')}")
            print("\nApplicant Information:")
            print(f"  2a - Name, Vorname: {data.get('field_2a', '')}")
            print(f"  2b - Kostenstelle: {data.get('field_2b', '')}")
            print(f"  2c - Abteilung: {data.get('field_2c', '')}")
            print(f"  2d - E-Mail: {data.get('field_2d', '')}")
            print(f"  3  - Telefon: {data.get('field_3', '')}")
            print(f"  4  - Projektname/Projektnummer: {data.get('field_4', '')}")
            print(f"  5  - Triebwerk: {data.get('field_5', '')}")
            print(f"  6  - Bereich: {data.get('field_6', '')}")
            print(f"  7  - Datum: {data.get('field_7', '')}")
            print(f"  8  - Benötigtes Datum: {data.get('field_8', '')}")
            print(f"  9  - Verwendungszweck: {data.get('field_9', '')}")
            print(f"  10 - Benennung des Teils/Stoffes: {data.get('field_10', '')}")
            print(f"  11 - Lieferant: {data.get('field_11', '')}")
            print(f"  12a- Teilenummer/Typbezeichnung: {data.get('field_12a', '')}")
            print(f"  12b- Menge: {data.get('field_12b', '')}")
            print(f"  13 - Bemerkungen: {data.get('field_13', '')}")
            print(f"  14 - Dringlichkeit: {data.get('field_14', '')}")
            print(f"  15a- SAP-Material: {data.get('field_15a', '')}")
            print(f"  15b- Lagerbestand: {data.get('field_15b', '')}")
            print(f"  16 - Gültigkeitsdauer: {data.get('field_16', '')}")
            print(f"  17a- Lagerfähigkeit: {data.get('field_17a', '')}")
            print(f"  17b- Lagerbedingungen: {data.get('field_17b', '')}")
            print(f"  17c- Entsorgung: {data.get('field_17c', '')}")
            print(f"  18 - Einsatzort: {data.get('field_18', '')}")
            print(f"  19 - Sicherheitsdatenblatt beiliegend: {data.get('field_19', '')}")
            print(f"  20 - Alternativprodukt: {data.get('field_20', '')}")
            print(f"  21 - Verwendung seit: {data.get('field_21', '')}")
            print("="*80)
            print("Note: This is a console output only. No database or PDF operations performed yet.")
            print("="*80 + "\n")
            
            return JsonResponse({
                'success': True,
                'message': 'Antrag erfolgreich eingereicht!',
                'antragnummer': antragnummer
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            })
        except Exception as e:
            print(f"Error processing open request: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': 'Internal server error'
            })
    
    # GET request - display the form
    context = {
        'page_title': _('Open Request'),
        'description': _('Submit a request for materials, chemicals, or support - accessible to all users'),
    }
    return render(request, 'normieapp/open_request.html', context) 