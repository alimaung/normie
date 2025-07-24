import json
import subprocess
import os
from pathlib import Path

def load_original_user_list():
    """Load the original user list to get full user information"""
    with open('list.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_surname(surname):
    """Normalize surname for filename matching"""
    return surname.replace(' ', '_').replace('/', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')

def check_user_exists(file_path):
    """Simple check to see if user exists based on content patterns"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for empty data array (user doesn't exist)
        if '"data":[]' in content:
            return False
        
        # Check for data array with content (user exists)
        user_indicators = [
            '"firstName":', 
            '"lastName":', 
            '"email":', 
            '"username":',
            '"enabled":',
            '"authStatus":'
        ]
        
        # If we find user fields, the user likely exists
        found_indicators = sum(1 for indicator in user_indicators if indicator in content)
        
        if found_indicators >= 3:  # At least 3 user fields found
            return True
        
        # Check if "data":[{ pattern exists (even if truncated)
        if '"data":[{' in content:
            return True
            
        return False
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def find_nonexisting_users():
    """Find users that don't exist in ChemScan"""
    users_dir = Path('users')
    if not users_dir.exists():
        print("Users directory does not exist! Run requester.py first.")
        return []
    
    # Load original user list for reference
    original_users = load_original_user_list()
    
    # Create lookup by normalized surname
    user_lookup = {}
    for user in original_users:
        normalized_surname = normalize_surname(user['surname'])
        user_lookup[normalized_surname] = user
    
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
        user_exists = check_user_exists(html_file)
        
        if user_exists is None:
            print(f"Could not parse {html_file}")
            continue
        
        if not user_exists:
            nonexisting_users.append(original_user)
            print(f"✗ Non-existing: {original_user['name']} {original_user['surname']}")
    
    return nonexisting_users

def create_user_account(user, script_path):
    """Create a ChemScan account for a user using the PowerShell script"""
    try:
        # Execute the PowerShell script with user parameters
        result = subprocess.run([
            'powershell.exe', 
            '-ExecutionPolicy', 'Bypass',
            '-File', script_path,
            '-Name', user['name'],
            '-Surname', user['surname'],
            '-Email', user['email']
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            return {
                'success': True,
                'output': result.stdout,
                'error': None
            }
        else:
            return {
                'success': False,
                'output': result.stdout,
                'error': result.stderr
            }
            
    except Exception as e:
        return {
            'success': False,
            'output': None,
            'error': str(e)
        }

def save_creation_results(results):
    """Save the user creation results to a JSON file"""
    output_file = 'user_creation_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Creation results saved to: {output_file}")

def main():
    """Main function to create missing user accounts"""
    print("Finding non-existing users...")
    
    # Find users that don't exist
    nonexisting_users = find_nonexisting_users()
    
    if not nonexisting_users:
        print("No non-existing users found!")
        return
    
    print(f"\nFound {len(nonexisting_users)} users that need to be created:")
    for user in nonexisting_users:
        print(f"- {user['name']} {user['surname']} ({user['email']})")
    
    # Ask for confirmation
    response = input(f"\nDo you want to create {len(nonexisting_users)} user accounts? (y/N): ")
    if response.lower() != 'y':
        print("User creation cancelled.")
        return
    
    script_path = 'create_user.ps1'
    if not os.path.exists(script_path):
        print(f"PowerShell script {script_path} not found!")
        return
    
    print(f"\nCreating {len(nonexisting_users)} user accounts...")
    
    results = {
        'summary': {
            'total_attempted': len(nonexisting_users),
            'successful': 0,
            'failed': 0
        },
        'created_users': [],
        'failed_users': []
    }
    
    # Create each user account
    for i, user in enumerate(nonexisting_users, 1):
        print(f"\nCreating user {i}/{len(nonexisting_users)}: {user['name']} {user['surname']}")
        
        result = create_user_account(user, script_path)
        
        user_result = {
            'name': user['name'],
            'surname': user['surname'],
            'email': user['email'],
            'success': result['success'],
            'output': result['output'],
            'error': result['error']
        }
        
        if result['success']:
            results['created_users'].append(user_result)
            results['summary']['successful'] += 1
            print(f"✓ Successfully created: {user['name']} {user['surname']}")
        else:
            results['failed_users'].append(user_result)
            results['summary']['failed'] += 1
            print(f"✗ Failed to create: {user['name']} {user['surname']}")
            if result['error']:
                print(f"  Error: {result['error']}")
        
        print("-" * 50)
    
    # Save results
    save_creation_results(results)
    
    # Print summary
    print(f"\n=== CREATION SUMMARY ===")
    print(f"Total attempted: {results['summary']['total_attempted']}")
    print(f"Successfully created: {results['summary']['successful']}")
    print(f"Failed: {results['summary']['failed']}")
    
    if results['created_users']:
        print(f"\n=== SUCCESSFULLY CREATED ===")
        for user in results['created_users']:
            print(f"- {user['name']} {user['surname']} ({user['email']})")
    
    if results['failed_users']:
        print(f"\n=== FAILED TO CREATE ===")
        for user in results['failed_users']:
            print(f"- {user['name']} {user['surname']} ({user['email']})")

if __name__ == "__main__":
    main() 