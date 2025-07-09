from django.shortcuts import render
from django.http import Http404
from django.utils.translation import gettext as _
from ..decorators import restrict_read_only_users
import json
import os
from django.conf import settings


@restrict_read_only_users
def tkz(request):
    """
    TKZ parts directory page view - requires applicant role or above.
    """
    return render(request, 'normieapp/tkz.html')


@restrict_read_only_users
def tkz_detail(request, row_number):
    """
    Display detailed view of a specific TKZ part by row number.
    """
    # Load the JSON data
    json_path = os.path.join(settings.BASE_DIR, 'normieapp', 'static', 'normieapp', 'data', 'TKZ.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get item by row number (1-indexed)
        # Sort data same way as frontend (by Part Number ascending)
        data_array = data.get('data', [])
        
        # Sort by Part Number ascending (same as frontend default)
        def parse_part_no(part_no):
            if not part_no or not isinstance(part_no, str):
                return (0,)
            try:
                # Convert to integer for proper numeric sorting
                return (int(part_no),)
            except ValueError:
                # If conversion fails, use string sorting
                return (part_no,)
        
        sorted_data = sorted(data_array, key=lambda x: parse_part_no(x.get('Teilenummer', '')))
        
        if row_number < 1 or row_number > len(sorted_data):
            raise Http404("TKZ part not found")
        
        item = sorted_data[row_number - 1]  # Convert to 0-indexed
        
        # Create template-friendly version of item data
        template_item = {
            'raw_data': item,
            'teilenummer': item.get('Teilenummer', ''),
            'to_nummer': item.get('TO-Nummer', ''),
            'kategorie': item.get('Benennung / Kategorie', ''),
            'titel': item.get('Normkurzbezeichnung / Titel', ''),
            'projekt': item.get('Projekt ', ''),  # Note the space in the key
            'name': item.get('Name', ''),
            'abteilung': item.get('Abteilung', ''),
            'datum': item.get('Datum', ''),
            'bemerkungen': item.get('Bemerkungen:', ''),
            'ben_en': item.get('BEN_EN', ''),
            'zusatzinfo': item.get('Zusatzinfo', ''),
        }
        
        context = {
            'item': template_item,
            'row_number': row_number,
            'total_parts': len(sorted_data),
        }
        
        return render(request, 'normieapp/tkz_detail.html', context)
        
    except FileNotFoundError:
        raise Http404("TKZ data not found")
    except json.JSONDecodeError:
        raise Http404("TKZ data is corrupted")
    except Exception as e:
        # Log the error in a real application
        raise Http404("Error loading TKZ data") 