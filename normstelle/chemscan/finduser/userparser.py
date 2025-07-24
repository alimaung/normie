import re
import json
from bs4 import BeautifulSoup
from pathlib import Path
import os

def parse_header_info(soup):
    """Extract name, surname, and status from header section"""
    header_info = {
        'name': None,
        'surname': None,
        'full_name': None,
        'status_enabled': False,
        'status_active': False
    }
    
    try:
        # Extract full name from h1 with class page-title__entity-title
        title_element = soup.find('h1', class_='page-title__entity-title')
        if title_element:
            full_name = title_element.get_text(strip=True)
            header_info['full_name'] = full_name
            
            # Try to split into name and surname (assuming "First Last" format)
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                header_info['name'] = name_parts[0]
                header_info['surname'] = ' '.join(name_parts[1:])  # Handle multiple surnames
            elif len(name_parts) == 1:
                header_info['name'] = name_parts[0]
        
        # Check status badges
        status_spans = soup.find_all('span', class_='badge')
        for span in status_spans:
            text = span.get_text(strip=True)
            if 'Aktiviert' in text or 'Enabled' in text:
                header_info['status_enabled'] = True
            if 'Active' in text:
                header_info['status_active'] = True
                
    except Exception as e:
        print(f"Error parsing header info: {e}")
    
    return header_info

def parse_block_attributes(soup):
    """Extract attributes from the responsive-block section"""
    block_info = {
        'username': None,
        'birthday': None,
        'email': None,
        'phone': None,
        'roles': None,
        'groups': None,
        'business_units': None,
        'title': None,
        'signature': None
    }
    
    try:
        # Find all attribute items
        attribute_items = soup.find_all('div', class_='attribute-item')
        
        for item in attribute_items:
            # Get the label (term)
            label_element = item.find('label', class_='attribute-item__term')
            if not label_element:
                continue
                
            label = label_element.get_text(strip=True)
            
            # Get the value (description)
            desc_element = item.find('div', class_='attribute-item__description')
            if not desc_element:
                continue
            
            # Extract value based on label
            if 'Benutzername' in label or 'Username' in label:
                control_label = desc_element.find('div', class_='control-label')
                if control_label:
                    block_info['username'] = control_label.get_text(strip=True)
                    
            elif 'Geburtstag' in label or 'Birthday' in label:
                control_label = desc_element.find('div', class_='control-label')
                if control_label:
                    text = control_label.get_text(strip=True)
                    block_info['birthday'] = None if 'Nicht verfügbar' in text or 'Not available' in text else text
                    
            elif 'E-Mail' in label or 'Email' in label:
                # Look for email link
                email_link = desc_element.find('a', class_='email')
                if email_link:
                    bdo = email_link.find('bdo')
                    if bdo:
                        block_info['email'] = bdo.get_text(strip=True)
                    else:
                        block_info['email'] = email_link.get_text(strip=True)
                        
            elif 'Telefon' in label or 'Phone' in label:
                control_label = desc_element.find('div', class_='control-label')
                if control_label:
                    text = control_label.get_text(strip=True)
                    block_info['phone'] = None if 'Nicht verfügbar' in text or 'Not available' in text else text
                    
            elif 'Rollen' in label or 'Roles' in label:
                control_label = desc_element.find('div', class_='control-label')
                if control_label:
                    text = control_label.get_text(strip=True)
                    block_info['roles'] = None if 'Nicht verfügbar' in text or 'Not available' in text else text
                    
            elif 'Gruppen' in label or 'Groups' in label:
                control_label = desc_element.find('div', class_='control-label')
                if control_label:
                    text = control_label.get_text(strip=True)
                    block_info['groups'] = None if 'Nicht verfügbar' in text or 'Not available' in text else text
                    
            elif 'Unternehmenseinheiten' in label or 'Business Units' in label:
                control_label = desc_element.find('div', class_='control-label')
                if control_label:
                    text = control_label.get_text(strip=True)
                    block_info['business_units'] = None if 'Nicht verfügbar' in text or 'Not available' in text else text
                    
            elif 'Titel' in label or 'Title' in label:
                control_label = desc_element.find('div', class_='control-label')
                if control_label:
                    text = control_label.get_text(strip=True)
                    block_info['title'] = None if 'Nicht verfügbar' in text or 'Not available' in text else text
                    
            elif 'Unterschrift' in label or 'Signature' in label:
                control_label = desc_element.find('div', class_='control-label')
                if control_label:
                    text = control_label.get_text(strip=True)
                    block_info['signature'] = None if 'Nicht verfügbar' in text or 'Not available' in text else text
                    
    except Exception as e:
        print(f"Error parsing block attributes: {e}")
    
    return block_info

def parse_inline_info(soup):
    """Extract creation, update, and login information from inline section"""
    inline_info = {
        'created_at': None,
        'updated_at': None,
        'last_login': None,
        'login_count': None,
        'owner': None
    }
    
    try:
        # Find the inline info section
        inline_section = soup.find('div', class_='row inline-info')
        if not inline_section:
            return inline_info
        
        # Parse left side (timestamps and login info)
        left_side = inline_section.find('ul', class_='inline')
        if left_side:
            items = left_side.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                
                if 'Erstellt am:' in text or 'Created:' in text:
                    # Extract date after the colon
                    match = re.search(r'(?:Erstellt am:|Created:)\s*(.+)', text)
                    if match:
                        inline_info['created_at'] = match.group(1).strip()
                        
                elif 'Aktualisiert am:' in text or 'Updated:' in text:
                    match = re.search(r'(?:Aktualisiert am:|Updated:)\s*(.+)', text)
                    if match:
                        inline_info['updated_at'] = match.group(1).strip()
                        
                elif 'Zuletzt angemeldet:' in text or 'Last login:' in text:
                    match = re.search(r'(?:Zuletzt angemeldet:|Last login:)\s*(.+)', text)
                    if match:
                        inline_info['last_login'] = match.group(1).strip()
                        
                elif 'Anzahl Anmeldungen:' in text or 'Login count:' in text:
                    match = re.search(r'(?:Anzahl Anmeldungen:|Login count:)\s*(\d+)', text)
                    if match:
                        inline_info['login_count'] = int(match.group(1))
        
        # Parse right side (owner information)
        right_side = inline_section.find('div', class_='pull-right')
        if right_side:
            owner_link = right_side.find('a')
            if owner_link:
                inline_info['owner'] = owner_link.get_text(strip=True)
                
    except Exception as e:
        print(f"Error parsing inline info: {e}")
    
    return inline_info

def parse_user_html(html_content):
    """Parse complete user HTML and extract all information"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract information from different sections
        header_info = parse_header_info(soup)
        block_info = parse_block_attributes(soup)
        inline_info = parse_inline_info(soup)
        
        # Combine all information
        user_data = {
            **header_info,
            **block_info,
            **inline_info
        }
        
        return user_data
        
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None

def parse_user_file(file_path):
    """Parse a user HTML file and return extracted information"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        user_data = parse_user_html(html_content)
        
        if user_data:
            # Add file information
            user_data['source_file'] = str(file_path)
            user_data['user_id'] = extract_user_id_from_filename(file_path)
        
        return user_data
        
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def extract_user_id_from_filename(file_path):
    """Extract user ID from filename like 'user_123.html'"""
    try:
        filename = Path(file_path).stem
        match = re.search(r'user_(\d+)', filename)
        if match:
            return int(match.group(1))
    except:
        pass
    return None

def parse_all_users_in_directory(users_dir='users'):
    """Parse all user HTML files in a directory"""
    users_dir = Path(users_dir)
    if not users_dir.exists():
        print(f"Directory {users_dir} does not exist!")
        return []
    
    all_users = []
    html_files = list(users_dir.glob('*.html'))
    
    print(f"Found {len(html_files)} HTML files to parse...")
    
    for i, file_path in enumerate(html_files, 1):
        print(f"Parsing {i}/{len(html_files)}: {file_path.name}")
        
        user_data = parse_user_file(file_path)
        if user_data:
            all_users.append(user_data)
        else:
            print(f"  ✗ Failed to parse {file_path.name}")
    
    return all_users

def save_parsed_users(users_data, output_file='parsed_users.json'):
    """Save parsed user data to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        print(f"Parsed user data saved to {output_file}")
    except Exception as e:
        print(f"Error saving data: {e}")

def main():
    """Main function to parse all users and save results"""
    print("Starting user HTML parsing...")
    
    # Parse all users
    users_data = parse_all_users_in_directory('users')
    
    if not users_data:
        print("No users parsed successfully!")
        return
    
    print(f"\nSuccessfully parsed {len(users_data)} users")
    
    # Save to JSON
    save_parsed_users(users_data, 'parsed_users.json')
    
    # Print summary
    print("\n" + "=" * 50)
    print("PARSING SUMMARY")
    print("=" * 50)
    print(f"Total users parsed: {len(users_data)}")
    
    # Count by role
    roles = {}
    for user in users_data:
        role = user.get('roles', 'Unknown')
        roles[role] = roles.get(role, 0) + 1
    
    print(f"\nUsers by role:")
    for role, count in sorted(roles.items()):
        print(f"  - {role}: {count}")
    
    # Sample data
    print(f"\nSample user data:")
    if users_data:
        sample = users_data[0]
        print(f"  Name: {sample.get('full_name', 'N/A')}")
        print(f"  Email: {sample.get('email', 'N/A')}")
        print(f"  Role: {sample.get('roles', 'N/A')}")
        print(f"  Title: {sample.get('title', 'N/A')}")
        print(f"  Status: {'Active' if sample.get('status_active') else 'Inactive'}")

if __name__ == "__main__":
    main()
