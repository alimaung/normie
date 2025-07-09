from django.shortcuts import render
from django.http import Http404
from django.utils.translation import gettext as _
from ..decorators import restrict_read_only_users
import json
import os
from django.conf import settings


@restrict_read_only_users
def directory(request):
    """
    Directory page view - requires applicant role or above.
    """
    return render(request, 'normieapp/directory.html')


@restrict_read_only_users
def directory_detail(request, row_number):
    """
    Display detailed view of a specific directory item by row number.
    """
    # Load the JSON data
    json_path = os.path.join(settings.BASE_DIR, 'normieapp', 'static', 'normieapp', 'data', 'Verzeichnis.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get item by row number (1-indexed)
        # Need to sort data same way as frontend (by Application No. descending)
        data_array = data.get('data', [])
        
        # Sort by Application No. descending (same as frontend default)
        def parse_app_no(app_no):
            if not app_no or not isinstance(app_no, str):
                return (0, 0)
            parts = app_no.split('/')
            if len(parts) != 2:
                return (0, 0)
            try:
                return (int(parts[1]), int(parts[0]))  # year first, then number
            except ValueError:
                return (0, 0)
        
        sorted_data = sorted(data_array, key=lambda x: parse_app_no(x.get('Antrag-nummer', '')), reverse=True)
        
        if row_number < 1 or row_number > len(sorted_data):
            raise Http404("Directory item not found")
        
        item = sorted_data[row_number - 1]  # Convert to 0-indexed
        
        # Get color mapping for status
        color_mapping = data.get('metadata', {}).get('color_mapping', {})
        
        # Map color to status class
        status_class_map = {
            "#CCFFCC": "approved",
            "#CCFF99": "first-use", 
            "#FFCC99": "rejected",
            "#FFFFFF": "processing"
        }
        status_class = status_class_map.get(item.get('color', ''), 'processing')
        
        # Create template-friendly version of item data
        template_item = {
            'raw_data': item,
            'antrag_nummer': item.get('Antrag-nummer', ''),
            'teile_nummer': item.get('Teile-nummer', ''),
            'freigabe': item.get('Freigabe', ''),
            'aircraft_relevant': item.get('relevant für Luftfahrtteile', ''),
            'benennung': item.get('Benennung', ''),
            'produktname': item.get('Produktname / Normkurzbezeichnung', ''),
            'produktzulassungs_spezifikation': item.get('Produktzulassungs-spezifikation', ''),
            'eingang': item.get('Eingang', ''),
            'abschluss': item.get('Abschluss', ''),
            'abteilung': item.get('Abteilung', ''),
            'einsatzort': item.get('Einsatzort', ''),
            'antragsteller': item.get('Antragsteller', ''),
            'bearbeiter': item.get('Bearbeiter', ''),
            'datum': item.get('Datum', ''),
            'bemerkung': item.get('Bemerkung \n(310 offene Anträge)', ''),
            'color': item.get('color', ''),
            'status': item.get('status', ''),
            # Documents
            'antrag_doc': item.get('Antrag'),
            'datenblatt': item.get('Datenblatt'),
            'produkt_zulassung': item.get('Produkt-zulassung'),
            'sdb_msds': item.get('SDB MSDS'),
            'gefährdungsprüfung_beurteilung': item.get('Gefährdungsprüfungeurteilung'),
            'gefährdungsprüfung': item.get('Gefährdungsprüfung'),
            'sonstiges': item.get('Sonstiges'),
            'schriftverkehr': item.get('Schriftverkehr'),
            'änderungshistorie': item.get('Änd. Historie'),
        }
        
        context = {
            'item': template_item,
            'color_mapping': color_mapping,
            'row_number': row_number,
            'status_class': status_class,
        }
        
        return render(request, 'normieapp/directory_detail.html', context)
        
    except FileNotFoundError:
        raise Http404("Directory data not found")


@restrict_read_only_users
def chemscan(request):
    """
    ChemScan analysis and management view - requires applicant role or above.
    """
    context = {
        'page_title': _('ChemScan Analysis'),
        'analysis_stats': {
            'total_scans': 1247,
            'pending_review': 23,
            'approved_substances': 892,
            'flagged_substances': 15
        },
        'recent_scans': [
            {'id': 'CS-001', 'substance': 'Acetone', 'status': 'Approved', 'risk_level': 'Low', 'date': '2024-03-15'},
            {'id': 'CS-002', 'substance': 'Methylene Chloride', 'status': 'Flagged', 'risk_level': 'High', 'date': '2024-03-14'},
            {'id': 'CS-003', 'substance': 'Isopropanol', 'status': 'Pending', 'risk_level': 'Medium', 'date': '2024-03-13'},
            {'id': 'CS-004', 'substance': 'Toluene', 'status': 'Under Review', 'risk_level': 'Medium', 'date': '2024-03-12'},
        ]
    }
    return render(request, 'normieapp/chemscan.html', context)


@restrict_read_only_users
def requests_page(request):
    """
    Requests page view - requires applicant role or above.
    This will be a comprehensive requests management page to be built later.
    """
    context = {
        'page_title': _('Requests Management'),
    }
    return render(request, 'normieapp/requests.html', context) 