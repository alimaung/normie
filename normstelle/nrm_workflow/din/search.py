import subprocess
import os
import sys
from bs4 import BeautifulSoup
import json
from pathlib import Path

def execute_powershell_script():
    """Execute the PowerShell script and return success status"""
ps_script = "search.ps1"

    if not os.path.exists(ps_script):
        print(f"❌ PowerShell script not found: {ps_script}")
        return False
    
    print(f"🔄 Executing PowerShell script: {ps_script}")
    
    try:
        # Try different PowerShell executables
        powershell_commands = [
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ps_script],
            ["pwsh.exe", "-ExecutionPolicy", "Bypass", "-File", ps_script],
            ["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ps_script]
        ]
        
        for cmd in powershell_commands:
            try:
                print(f"  Trying: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print(f"  ✅ PowerShell script executed successfully")
                    if result.stdout:
                        print(f"  📝 STDOUT: {result.stdout[:200]}...")
                    return True
                else:
                    print(f"  ❌ Script failed with return code: {result.returncode}")
                    if result.stderr:
                        print(f"  🔴 STDERR: {result.stderr[:200]}...")
                    
            except subprocess.TimeoutExpired:
                print(f"  ⏰ Timeout executing: {cmd[0]}")
            except FileNotFoundError:
                print(f"  📂 Not found: {cmd[0]}")
            except Exception as e:
                print(f"  ⚠️ Exception with {cmd[0]}: {e}")
        
        print("❌ All PowerShell execution attempts failed")
        return False
        
    except Exception as e:
        print(f"❌ Error executing PowerShell script: {e}")
        return False

def read_html_response():
    """Read and return the HTML response file"""
    html_file = "search.html"
    
    if not os.path.exists(html_file):
        print(f"❌ HTML response file not found: {html_file}")
        return None
    
    print(f"📖 Reading HTML response: {html_file}")
    
    # Try different encodings
    encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'latin1']
    
    for encoding in encodings:
        try:
            with open(html_file, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"  ✅ Successfully read with {encoding} encoding")
            print(f"  📏 Content length: {len(content)} characters")
            return content
        except UnicodeDecodeError as e:
            print(f"  ❌ Failed with {encoding}: {e}")
        except Exception as e:
            print(f"  ⚠️ Error with {encoding}: {e}")
    
    print("❌ Could not read HTML file with any encoding")
    return None

def parse_din_standards(html_content):
    """Parse the HTML content and extract DIN standards information"""
    if not html_content:
        return []
    
    print("🔍 Parsing HTML content for DIN standards...")
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        standards = []
        
        # Debug: Let's see what we actually have in the HTML
        print("  🔍 Debugging HTML structure...")
        
        # Look for the specific list structure from list.html
        list_container = soup.find('ul', class_='bwr-card-group bwr-card-group--list')
        if list_container:
            print(f"  ✅ Found list container: {list_container.name} with classes {list_container.get('class')}")
            # Find list items
            list_items = list_container.find_all('li', class_='bwr-card-group__list-item')
            print(f"  📊 Found {len(list_items)} list items")
            
            for i, item in enumerate(list_items, 1):
                # Within each list item, find the card
                card = item.find('div', class_='bwr-card')
                if card:
                    print(f"    ✅ Found card {i} in list item")
                else:
                    print(f"    ❌ No card found in list item {i}")
        else:
            print("  ❌ No list container found, looking for individual cards...")
            # Fallback: Look for cards directly
            cards = soup.find_all('div', class_='bwr-card')
            print(f"  📊 Found {len(cards)} direct card elements")
            
            # Also try the full class name
            full_class_cards = soup.find_all('div', class_='bwr-card bwr-card--list js-card')
            print(f"  📊 Found {len(full_class_cards)} cards with full class name")
            
            # Debug: Search for key terms in the HTML
            print(f"  🔍 Searching HTML content for key terms...")
            key_terms = ['ASTM', 'E 192', 'bwr-card', 'list-item', 'Standard Reference']
            for term in key_terms:
                count = html_content.lower().count(term.lower())
                print(f"    '{term}': found {count} times")
            
            # Debug: Show some of the HTML structure
            if len(html_content) > 1000:
                print(f"  📄 HTML sample (first 500 chars): {html_content[:500]}...")
                print(f"  📄 HTML sample (last 500 chars): ...{html_content[-500:]}")
            else:
                print(f"  📄 Full HTML content: {html_content}")
        
        # Try multiple strategies to find the results in the full HTML page
        cards_to_process = []
        
        # Strategy 1: Look for list items directly (they're definitely in the HTML!)
        print("  🔍 Searching for 'bwr-card-group__list-item' class...")
        list_items = soup.find_all('li', class_='bwr-card-group__list-item')
        
        if not list_items:
            # Try partial class matching
            print("  🔍 Trying partial class matching for list items...")
            all_lis = soup.find_all('li')
            print(f"    Found {len(all_lis)} total <li> elements")
            
            for li in all_lis:
                li_classes = li.get('class', [])
                if li_classes:
                    print(f"    <li> classes: {li_classes}")
                    if 'bwr-card-group__list-item' in li_classes:
                        list_items.append(li)
                        print(f"    ✅ Found matching li with exact class")
        
        if list_items:
            print(f"  ✅ Found {len(list_items)} list items with class 'bwr-card-group__list-item'")
            for item in list_items:
                card = item.find('div', class_='bwr-card')
                if card:
                    cards_to_process.append(card)
                    print(f"    ✅ Found card in list item")
                else:
                    print(f"    ⚠️ List item found but no card div inside")
        else:
            print("  ❌ No list items found with 'bwr-card-group__list-item' class")
        
        # Strategy 1b: Also check for the container approach
        if not cards_to_process:
            list_container = soup.find('ul', class_='bwr-card-group bwr-card-group--list')
            if list_container:
                print("  ✅ Found snippet-style list container")
                container_items = list_container.find_all('li', class_='bwr-card-group__list-item')
                for item in container_items:
                    card = item.find('div', class_='bwr-card bwr-card--list js-card')
                    if not card:
                        card = item.find('div', class_='bwr-card')
                    if card:
                        cards_to_process.append(card)
        
        # Strategy 2: Look for results in a search results container
        if not cards_to_process:
            print("  🔍 Looking for search results containers...")
            
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
                    print(f"    🔍 Checking container: {container.name} {container.get('class', [])} {container.get('id', '')}")
                    
                    # Look for cards in this container
                    container_cards = container.find_all('div', class_='bwr-card bwr-card--list js-card')
                    if not container_cards:
                        container_cards = container.find_all('div', class_='bwr-card')
                    
                    if container_cards:
                        print(f"    ✅ Found {len(container_cards)} cards in this container")
                        cards_to_process.extend(container_cards)
                        break
        
        # Strategy 3: Look for any cards in the entire document
        if not cards_to_process:
            print("  🔍 Searching entire document for cards...")
            cards_to_process = soup.find_all('div', class_='bwr-card bwr-card--list js-card')
            if not cards_to_process:
                cards_to_process = soup.find_all('div', class_='bwr-card')
                
        # Strategy 4: Look for alternative card patterns that might be used
        if not cards_to_process:
            print("  🔍 Looking for alternative card patterns...")
            
            # Try different class patterns
            alternative_patterns = [
                {'class': lambda x: x and 'card' in ' '.join(x).lower()},
                {'class': lambda x: x and 'product' in ' '.join(x).lower()},
                {'class': lambda x: x and 'item' in ' '.join(x).lower()},
                {'class': lambda x: x and 'result' in ' '.join(x).lower()},
            ]
            
            for pattern in alternative_patterns:
                alt_cards = soup.find_all('div', pattern)
                if alt_cards:
                    print(f"    🔍 Found {len(alt_cards)} elements with pattern {pattern}")
                    # Check if these look like product cards
                    for card in alt_cards[:3]:  # Check first 3
                        if card.find('a') and (card.find(class_=lambda x: x and 'title' in ' '.join(x).lower() if x else False) or 
                                              card.find(class_=lambda x: x and 'price' in ' '.join(x).lower() if x else False)):
                            print(f"    ✅ Alternative cards look like product cards")
                            cards_to_process = alt_cards
                            break
                    if cards_to_process:
                        break
        
        print(f"  📊 Processing {len(cards_to_process)} cards for data extraction")
        
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
                    print(f"    ✅ Parsed standard {i}: {standard.get('title', 'Unknown')}")
                else:
                    print(f"    ⚠️ Card {i}: Missing essential information")
                    
            except Exception as e:
                print(f"    ❌ Error parsing card {i}: {e}")
                continue
        
        print(f"  🎯 Successfully parsed {len(standards)} standards")
        return standards
        
    except Exception as e:
        print(f"❌ Error parsing HTML: {e}")
        return []

def print_standards_list(standards):
    """Print a formatted list of the parsed standards"""
    if not standards:
        print("📭 No standards found to display")
        return
    
    print(f"\n{'='*80}")
    print(f"🎯 PARSED DIN STANDARDS LIST ({len(standards)} items)")
    print(f"{'='*80}")
    
    for standard in standards:
        print(f"\n📋 Standard #{standard.get('index', '?')}")
        print(f"  📑 Title: {standard.get('title', 'N/A')}")
        
        if standard.get('description'):
            print(f"  📝 Description: {standard.get('description')}")
        
        if standard.get('status'):
            print(f"  🏷️  Status: {standard.get('status')}")
        
        if standard.get('year'):
            print(f"  📅 Year: {standard.get('year')}")
        
        if standard.get('price_vat'):
            print(f"  💰 Price (VAT incl.): {standard.get('price_vat')}")
        
        if standard.get('price_no_vat'):
            print(f"  💸 Price (VAT excl.): {standard.get('price_no_vat')}")
        
        if standard.get('url'):
            print(f"  🔗 URL: {standard.get('url')}")
        
        if standard.get('details'):
            details = standard.get('details')
            if len(details) > 100:
                details = details[:100] + "..."
            print(f"  📋 Details: {details}")
    
    print(f"\n{'='*80}")
    print(f"✅ Total standards displayed: {len(standards)}")
    print(f"{'='*80}")

def save_parsed_data(standards):
    """Save the parsed data to a JSON file"""
    if not standards:
        return
    
    output_file = "parsed_standards.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(standards, f, indent=2, ensure_ascii=False)
        print(f"💾 Parsed data saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")

def save_html_sample(html_content):
    """Save a sample of the HTML for debugging"""
    if not html_content:
        return
    
    # Save first 50KB for debugging
    sample_size = min(50000, len(html_content))
    sample_file = "html_sample_debug.html"
    
    try:
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(html_content[:sample_size])
        print(f"🔍 HTML sample saved to: {sample_file} (first {sample_size} chars)")
    except Exception as e:
        print(f"❌ Error saving HTML sample: {e}")

def test_list_html_parsing():
    """Test parsing with the existing list.html file"""
    print("🧪 Testing parser with list.html file")
    
    list_html_file = "list.html"
    if not os.path.exists(list_html_file):
        print(f"  ❌ list.html file not found: {list_html_file}")
        return []
    
    try:
        with open(list_html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        print(f"  ✅ Successfully read list.html ({len(html_content)} characters)")
        
        standards = parse_din_standards(html_content)
        print(f"  🎯 Parsed {len(standards)} standards from list.html")
        
        return standards
        
    except Exception as e:
        print(f"  ❌ Error reading list.html: {e}")
        return []

def main():
    """Main test function"""
    print("🚀 DIN Standards Search Test Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Step 0: Test with existing list.html file first
    print(f"\n🔸 Step 0: Test Parser with list.html")
    test_standards = test_list_html_parsing()
    if test_standards:
        print(f"  ✅ Parser test successful! Found {len(test_standards)} standards in list.html")
        print("  📋 Sample standard from list.html:")
        if test_standards:
            sample = test_standards[0]
            print(f"    Title: {sample.get('title', 'N/A')}")
            print(f"    Description: {sample.get('description', 'N/A')}")
            print(f"    Price: {sample.get('price_vat', 'N/A')}")
    else:
        print("  ⚠️ Parser test failed - check list.html structure")
    
    # Step 1: Execute PowerShell script
    print(f"\n🔸 Step 1: Execute PowerShell Script")
    ps_success = execute_powershell_script()
    
    # Step 2: Read HTML response
    print(f"\n🔸 Step 2: Read HTML Response")
    html_content = read_html_response()
    
    # Step 2.5: Save HTML sample for debugging
    if html_content:
        print(f"\n🔸 Step 2.5: Save HTML Sample for Debugging")
        save_html_sample(html_content)
    
    # Step 3: Parse standards
    print(f"\n🔸 Step 3: Parse Standards")
    standards = parse_din_standards(html_content)
    
    # Step 4: Display results
    print(f"\n🔸 Step 4: Display Results")
    print_standards_list(standards)
    
    # Step 5: Save data
    print(f"\n🔸 Step 5: Save Parsed Data")
    save_parsed_data(standards)
    
    # Summary
    print(f"\n🎯 TEST SUMMARY")
    print(f"  list.html parser test: {'✅ Success' if test_standards else '❌ Failed'}")
    print(f"  PowerShell execution: {'✅ Success' if ps_success else '❌ Failed'}")
    print(f"  HTML file read: {'✅ Success' if html_content else '❌ Failed'}")
    print(f"  Standards parsed: {len(standards)} items")
    
    if standards:
        print(f"\n🎉 Test completed successfully! Found {len(standards)} DIN standards.")
    elif test_standards:
        print(f"\n⚠️ Parser works with list.html but no standards found in PowerShell output.")
        print("   - The PowerShell script may not be returning the expected HTML structure")
    else:
        print(f"\n⚠️ Test completed but no standards were found.")
        if not ps_success:
            print("   - Check PowerShell execution policy and script permissions")
        if not html_content:
            print("   - Check if the HTML response file was generated")

if __name__ == "__main__":
    main()

