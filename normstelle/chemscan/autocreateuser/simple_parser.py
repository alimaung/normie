import json
import os
import re
from pathlib import Path

def load_original_user_list():
    """Load the original user list to get full user information"""
    with open('list.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_surname(surname):
    """Normalize surname for filename matching"""
    return surname.replace(' ', '_').replace('/', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')

def check_user_exists(file_path, expected_user):
    """Check if the specific expected user exists in the HTML response"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for empty data array (user doesn't exist)
        if '"data":[]' in content:
            return False
        
        # Extract the JSON content from the HTML response
        # Look for the Content line that contains the JSON data
        json_match = re.search(r'Content\s*:\s*({.*?"data":\[.*?\]})', content, re.DOTALL)
        if not json_match:
            # Fallback: look for JSON pattern directly
            json_match = re.search(r'{"data":\[.*?\]}', content, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1) if json_match.groups() else json_match.group(0)
            try:
                # Try to parse as JSON to extract user data
                data = json.loads(json_str)
                users_data = data.get('data', [])
                
                # Check if any user in the response matches our expected user
                for user in users_data:
                    # Match by email (most reliable)
                    if user.get('email', '').lower() == expected_user['email'].lower():
                        print(f"  → Found exact email match: {user.get('email')}")
                        return True
                    
                    # Match by first name and last name combination
                    first_name = user.get('firstName', '').lower()
                    last_name = user.get('lastName', '').lower()
                    expected_first = expected_user['name'].lower()
                    expected_last = expected_user['surname'].lower()
                    
                    if first_name == expected_first and last_name == expected_last:
                        print(f"  → Found name match: {first_name} {last_name}")
                        return True
                
                # If we have users but none match our expected user
                if users_data:
                    print(f"  → Found users but none match expected: {expected_user['name']} {expected_user['surname']} ({expected_user['email']})")
                    # Print what we found for debugging
                    for user in users_data:
                        print(f"    Found: {user.get('firstName', '')} {user.get('lastName', '')} ({user.get('email', '')})")
                    return False
                
            except json.JSONDecodeError:
                # If JSON parsing fails, fall back to string matching
                pass
        
        # Fallback to string matching if JSON parsing fails
        expected_email = expected_user['email'].lower()
        expected_first = expected_user['name'].lower()
        expected_last = expected_user['surname'].lower()
        content_lower = content.lower()
        
        # Check for email match
        if expected_email in content_lower:
            print(f"  → Found email in content: {expected_email}")
            return True
        
        # Check for name combination
        if expected_first in content_lower and expected_last in content_lower:
            print(f"  → Found name in content: {expected_first} {expected_last}")
            return True
        
        # If we find generic user data but not our specific user
        if '"data":[{' in content and '"firstName":' in content:
            print(f"  → Found other users but not {expected_user['name']} {expected_user['surname']}")
            return False
        
        return False
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def parse_users_simple():
    """Parse all user response files using simple string matching"""
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
        
        # Check if user exists
        user_exists = check_user_exists(html_file, original_user)
        
        if user_exists is None:
            print(f"Could not parse {html_file}")
            continue
        
        # Create user info
        user_info = {
            "name": original_user['name'],
            "surname": original_user['surname'],
            "email": original_user['email'],
            "filename": html_file.name
        }
        
        if user_exists:
            existing_users.append(user_info)
            print(f"✓ Found: {original_user['name']} {original_user['surname']}")
        else:
            nonexisting_users.append(user_info)
            print(f"✗ Not found: {original_user['name']} {original_user['surname']}")
    
    return existing_users, nonexisting_users

def main():
    """Main function to parse results and output JSON"""
    print("Parsing user response files with simple string matching...")
    
    existing_users, nonexisting_users = parse_users_simple()
    
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
    output_file = 'user_analysis_results_simple.json'
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