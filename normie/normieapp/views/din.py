from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.utils.translation import gettext as _
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..decorators import restrict_read_only_users
import json
import os
import subprocess
import tempfile
import re
from bs4 import BeautifulSoup
from django.conf import settings
import urllib.parse


@restrict_read_only_users
def din_search(request):
    """
    DIN Standards search page - requires applicant role or above.
    """
    context = {
        'page_title': _('DIN Standards Search'),
        'breadcrumbs': [
            {'name': _('Home'), 'url': '/'},
            {'name': _('Norms'), 'url': '#'},
            {'name': _('Standards Management'), 'url': '#'},
            {'name': _('Order Norm'), 'url': None}
        ]
    }
    return render(request, 'normieapp/din_search.html', context)


@restrict_read_only_users
@require_http_methods(["POST"])
def din_search_api(request):
    """
    API endpoint to execute DIN search via PowerShell script
    """
    try:
        query = request.POST.get('query', '').strip()
        hits_per_page = request.POST.get('hitsPerPage', '10')
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': _('Search query is required')
            })

        # Validate hits per page parameter
        if hits_per_page not in ['10', '25', '50', '100']:
            hits_per_page = '10'
        
        # Get the static PowerShell script path
        script_path = os.path.join(
            settings.BASE_DIR, 
            'normieapp', 
            'static', 
            'normieapp', 
            'scripts', 
            'din-search.ps1'
        )
        
        if not os.path.exists(script_path):
            return JsonResponse({
                'success': False,
                'error': _('Search script not found')
            })

        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'search.html')
            
            # Execute the PowerShell script with parameters
            try:
                # Use different PowerShell execution methods based on availability
                powershell_cmd = None
                for ps_exe in ['pwsh.exe', 'powershell.exe']:
                    try:
                        subprocess.run([ps_exe, '-Version'], capture_output=True, timeout=5)
                        powershell_cmd = ps_exe
                        break
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        continue
                
                if not powershell_cmd:
                    return JsonResponse({
                        'success': False,
                        'error': _('PowerShell not found on system')
                    })
                
                # Execute the script with parameters
                result = subprocess.run([
                    powershell_cmd,
                    '-ExecutionPolicy', 'Bypass',
                    '-NoProfile',
                    '-WindowStyle', 'Hidden',
                    '-File', script_path,
                    '-Query', query,
                    '-HitsPerPage', hits_per_page,
                    '-OutputFile', output_path
                ], capture_output=True, text=True, timeout=60, cwd=temp_dir)
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr else 'Unknown PowerShell error'
                    return JsonResponse({
                        'success': False,
                        'error': f'Script execution failed: {error_msg}'
                    })
                
                # Check if output file was created
                if not os.path.exists(output_path):
                    return JsonResponse({
                        'success': False,
                        'error': _('No search results file generated')
                    })
                
                # Parse the HTML results with proper encoding handling
                html_content = None
                # Try UTF-8 with BOM first since we're now writing with UTF-8 encoding
                for encoding in ['utf-8-sig', 'utf-8', 'cp1252', 'latin1']:
                    try:
                        with open(output_path, 'r', encoding=encoding) as f:
                            html_content = f.read()
                        # Successfully read the file
                        break
                    except (UnicodeDecodeError, UnicodeError):
                        continue
                
                if html_content is None:
                    return JsonResponse({
                        'success': False,
                        'error': _('Unable to read search results file')
                    })
                
                # Parse the results
                standards = parse_din_search_results(html_content)
                
                return JsonResponse({
                    'success': True,
                    'standards': standards,
                    'query': query,
                    'count': len(standards)
                })
                
            except subprocess.TimeoutExpired:
                return JsonResponse({
                    'success': False,
                    'error': _('Search request timed out')
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Execution error: {str(e)}'
                })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        })


def parse_din_search_results(html_content):
    """
    Parse the DIN search results HTML and extract standard information
    Using the proven working logic from search.py
    """
    standards = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        cards_to_process = []
        
        # Strategy 1: Look for list items directly (they're definitely in the HTML!)
        list_items = soup.find_all('li', class_='bwr-card-group__list-item')
        if list_items:
            for item in list_items:
                card = item.find('div', class_='bwr-card')
                if card:
                    cards_to_process.append(card)
        
        # Strategy 1b: Also check for the container approach
        if not cards_to_process:
            list_container = soup.find('ul', class_='bwr-card-group bwr-card-group--list')
            if list_container:
                container_items = list_container.find_all('li', class_='bwr-card-group__list-item')
                for item in container_items:
                    card = item.find('div', class_='bwr-card bwr-card--list js-card')
                    if not card:
                        card = item.find('div', class_='bwr-card')
                    if card:
                        cards_to_process.append(card)
        
        # Strategy 2: Look for results in a search results container
        if not cards_to_process:
            # Common search result container patterns
            result_containers = [
                soup.find('div', class_=lambda x: x and 'result' in x.lower()),
                soup.find('div', class_=lambda x: x and 'search' in x.lower()),
                soup.find('section', class_=lambda x: x and 'content' in x.lower()),
                soup.find('main'),
                soup.find('div', {'id': lambda x: x and 'result' in x.lower() if x else False}),
            ]
            
            for container in result_containers:
                if container:
                    # Look for cards in this container
                    container_cards = container.find_all('div', class_='bwr-card bwr-card--list js-card')
                    if not container_cards:
                        container_cards = container.find_all('div', class_='bwr-card')
                    
                    if container_cards:
                        cards_to_process.extend(container_cards)
                        break
        
        # Strategy 3: Look for any cards in the entire document
        if not cards_to_process:
            cards_to_process = soup.find_all('div', class_='bwr-card bwr-card--list js-card')
            if not cards_to_process:
                cards_to_process = soup.find_all('div', class_='bwr-card')
        
        # Process all found cards
        for i, card in enumerate(cards_to_process, 1):
            try:
                standard = {'index': i}
                
                # Extract title and standard number
                title_link = card.find('a', class_='bwr-card__title-link')
                if title_link:
                    standard['title'] = title_link.get_text(strip=True)
                    standard['url'] = title_link.get('href', '')
                    if standard['url'].startswith('/'):
                        standard['url'] = 'https://www.dinmedia.de' + standard['url']
                
                # Extract subtitle/description
                subtitle = card.find('p', class_='bwr-card__subtitle')
                if subtitle:
                    standard['description'] = subtitle.get_text(strip=True)
                
                # Extract additional details
                text_div = card.find('div', class_='bwr-card__text')
                if text_div:
                    paragraphs = text_div.find_all('p')
                    if paragraphs:
                        standard['details'] = paragraphs[0].get_text(strip=True)
                
                # Extract status and year
                type_elem = card.find('p', class_='bwr-type bwr-type--norm')
                if type_elem:
                    status_span = type_elem.find('span', class_='bwr-type__highlight--current')
                    if status_span:
                        standard['status'] = status_span.get_text(strip=True)
                    
                    year_span = type_elem.find('span', class_='bwr-type__item--light')
                    if year_span:
                        standard['year'] = year_span.get_text(strip=True)
                
                # Extract pricing
                buybox = card.find('div', class_='bwr-buybox')
                if buybox:
                    price_spans = buybox.find_all('span', class_='bwr-buybox__price-emph')
                    if price_spans:
                        # Get the price text and clean it up
                        vat_price_text = price_spans[0].get_text(strip=True)
                        standard['price_vat'] = vat_price_text
                        
                        if len(price_spans) > 1:
                            no_vat_price_text = price_spans[1].get_text(strip=True)
                            standard['price_no_vat'] = no_vat_price_text
                    
                    # Also get the price context (like "from" text)
                    price_paragraphs = buybox.find_all('p', class_='bwr-buybox__price')
                    if price_paragraphs:
                        vat_para = price_paragraphs[0].get_text(strip=True)
                        standard['price_vat_full'] = vat_para
                        
                        if len(price_paragraphs) > 1:
                            no_vat_para = price_paragraphs[1].get_text(strip=True)
                            standard['price_no_vat_full'] = no_vat_para
                
                # Extract image URL
                img = card.find('img', class_='bwr-picture__img')
                if img:
                    standard['image_url'] = img.get('src', '')
                    standard['image_alt'] = img.get('alt', '')
                
                # Only add if we have essential information
                if standard.get('title'):
                    standards.append(standard)
                    
            except Exception as e:
                # Continue parsing other cards even if one fails
                print(f"Error parsing card {i}: {e}")
                continue
    
    except Exception as e:
        print(f"Error parsing HTML: {e}")
    
    return standards


@restrict_read_only_users
def din_order(request):
    """
    DIN Standards ordering page
    """
    standard_id = request.GET.get('standard')
    context = {
        'page_title': _('Order DIN Standard'),
        'standard_id': standard_id,
        'breadcrumbs': [
            {'name': _('Home'), 'url': '/'},
            {'name': _('Norms'), 'url': '#'},
            {'name': _('Standards Management'), 'url': '#'},
            {'name': _('Order Norm'), 'url': None}
        ]
    }
    return render(request, 'normieapp/din_order.html', context)
