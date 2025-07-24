import json
import os
import re
from pathlib import Path

def extract_json_from_response(file_path):
    """Extract the JSON data from the PowerShell response file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the Content line - it may span multiple lines and be truncated
        content_match = re.search(r'Content\s*:\s*({.*?)(?=RawContent|$)', content, re.DOTALL)
        if content_match:
            json_str = content_match.group(1).strip()
            
            # The JSON might be truncated with "..." - let's try to reconstruct it
            if json_str.endswith('...'):
                # This is a truncated response, we need to extract what we can
                # Look for complete data entries
                if '"data":[' in json_str:
                    if json_str.count('[') > json_str.count(']'):
                        # Try to close the JSON properly for parsing
                        # Count how many objects seem to start but don't finish
                        open_braces = json_str.count('{') - json_str.count('}')
                        open_brackets = json_str.count('[') - json_str.count(']')
                        
                        # Try to close the structure
                        json_str = json_str.rstrip('...')
                        json_str += '}' * open_braces
                        json_str += ']' * open_brackets
            
            # Clean up and try to parse
            json_str = re.sub(r'\s+', ' ', json_str)
            return json.loads(json_str)
        
        # Alternative approach: look for any JSON-like structure
        json_match = re.search(r'({\"data\":\[.*?)}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            # If it's incomplete, try to complete it
            if not json_str.endswith('}'):
                json_str += '}'
            json_str = re.sub(r'\s+', ' ', json_str)
            return json.loads(json_str)
        
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error in {file_path}: {e}")
        # Try a simpler approach - just look for the data array
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if we can find "data":[] (empty) or "data":[{...}] (with data)
            if '"data":[]' in content:
                return {"data": []}
            elif '"data":[{' in content:
                return {"data": [{"exists": True}]}  # Simplified indicator
            
        except Exception:
            pass
        return None
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def load_original_user_list():
    """Load the original user list to get full user information"""
    with open('list.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_surname(surname):
    """Normalize surname for filename matching"""
    return surname.replace(' ', '_').replace('/', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')

def parse_users():
    """Parse all user response files and categorize as existing or non-existing"""
    users_dir = Path('users')
    if not users_dir.exists():
        print("Users directory does not exist!")
        return [], []
    
    # Load original user list for reference
    original_users = load_original_user_list()
    
    # Create lookup by normalized surname
    user_lookup = {}
    for user in original_users:
        normalized_surname = normalize_surname(user['surname'])
        user_lookup[normalized_surname] = user
    
    existing_users = []
    nonexisting_users = []
    
    # Process each HTML file in the users directory
    for html_file in users_dir.glob('*.html'):
        surname_key = html_file.stem  # filename without extension
        
        # Get original user data
        if surname_key not in user_lookup:
            print(f"Warning: No original user data found for {surname_key}")
            continue
            
        original_user = user_lookup[surname_key]
        
        # Extract JSON data from the response
        json_data = extract_json_from_response(html_file)
        
        if json_data is None:
            print(f"Could not extract JSON from {html_file}")
            continue
        
        # Check if user exists by looking at the data array
        user_info = {
            "name": original_user['name'],
            "surname": original_user['surname'],
            "email": original_user['email'],
            "filename": html_file.name
        }
        
        if 'data' in json_data and len(json_data['data']) > 0:
            # User exists - add the found data if available
            if isinstance(json_data['data'][0], dict) and 'exists' not in json_data['data'][0]:
                user_info['found_data'] = json_data['data'][0]  # Full data
            else:
                user_info['found_data'] = {"status": "exists_but_truncated"}
            existing_users.append(user_info)
            print(f"✓ Found: {original_user['name']} {original_user['surname']}")
        else:
            # User does not exist
            nonexisting_users.append(user_info)
            print(f"✗ Not found: {original_user['name']} {original_user['surname']}")
    
    return existing_users, nonexisting_users

def main():
    """Main function to parse results and output JSON"""
    print("Parsing user response files...")
    
    existing_users, nonexisting_users = parse_users()
    
    # Create the result structure
    result = {
        "summary": {
            "total_processed": len(existing_users) + len(nonexisting_users),
            "existing_count": len(existing_users),
            "nonexisting_count": len(nonexisting_users)
        },
        "existing_users": existing_users,
        "nonexisting_users": nonexisting_users
    }
    
    # Save to JSON file
    output_file = 'user_analysis_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total processed: {result['summary']['total_processed']}")
    print(f"Existing users: {result['summary']['existing_count']}")
    print(f"Non-existing users: {result['summary']['nonexisting_count']}")
    print(f"\nResults saved to: {output_file}")
    
    # Also print a simple overview
    print(f"\n=== EXISTING USERS ===")
    for user in existing_users:
        print(f"- {user['name']} {user['surname']} ({user['email']})")
    
    print(f"\n=== NON-EXISTING USERS ===")
    for user in nonexisting_users:
        print(f"- {user['name']} {user['surname']} ({user['email']})")

if __name__ == "__main__":
    main() 