import json
import subprocess
import time
import os
from pathlib import Path

def load_users_to_create():
    """Load the list of users to create from create.json"""
    try:
        with open('create.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: create.json file not found!")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing create.json: {e}")
        return []

def create_user_account(user, script_path):
    """Create a ChemScan account for a user using the create2.ps1 script"""
    try:
        # Execute the PowerShell script with user parameters
        result = subprocess.run([
            'powershell.exe', 
            '-ExecutionPolicy', 'Bypass',
            '-File', script_path,
            '-Name', user['name'],
            '-Surname', user['surname'],
            '-Email', user['email']
        ], capture_output=True, text=False)  # Get bytes to handle encoding issues
        
        # Handle encoding for stdout
        stdout_content = ""
        if result.stdout:
            try:
                stdout_content = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    stdout_content = result.stdout.decode('cp1252')  # Windows encoding
                except UnicodeDecodeError:
                    stdout_content = result.stdout.decode('utf-8', errors='replace')
        
        # Handle encoding for stderr
        stderr_content = ""
        if result.stderr:
            try:
                stderr_content = result.stderr.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    stderr_content = result.stderr.decode('cp1252')  # Windows encoding
                except UnicodeDecodeError:
                    stderr_content = result.stderr.decode('utf-8', errors='replace')
        
        # Determine success based on return code and response content
        success = result.returncode == 0
        
        # Check for specific success/error indicators in the response
        status_info = ""
        if "StatusCode" in stdout_content:
            if "200" in stdout_content:
                status_info = "HTTP 200 - Success"
            elif "400" in stdout_content:
                status_info = "HTTP 400 - Bad Request"
                success = False
            elif "401" in stdout_content:
                status_info = "HTTP 401 - Authentication failed"
                success = False
            elif "403" in stdout_content:
                status_info = "HTTP 403 - Forbidden"
                success = False
            elif "500" in stdout_content:
                status_info = "HTTP 500 - Server Error"
                success = False
        
        return {
            'success': success,
            'return_code': result.returncode,
            'stdout': stdout_content,
            'stderr': stderr_content,
            'status_info': status_info
        }
        
    except Exception as e:
        return {
            'success': False,
            'return_code': -1,
            'stdout': None,
            'stderr': None,
            'error': str(e),
            'status_info': f"Exception: {str(e)}"
        }

def save_creation_results(results):
    """Save the user creation results to a JSON file"""
    output_file = 'batch_creation_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Detailed results saved to: {output_file}")

def main():
    """Main function to create all users from create.json"""
    print("Loading users from create.json...")
    
    # Load users to create
    users_to_create = load_users_to_create()
    
    if not users_to_create:
        print("No users to create!")
        return
    
    print(f"Found {len(users_to_create)} users to create:")
    for user in users_to_create:
        print(f"- {user['name']} {user['surname']} ({user['email']})")
    
    # Ask for confirmation
    response = input(f"\nDo you want to create {len(users_to_create)} user accounts? (y/N): ")
    if response.lower() != 'y':
        print("User creation cancelled.")
        return
    
    script_path = 'create2.ps1'
    if not os.path.exists(script_path):
        print(f"PowerShell script {script_path} not found!")
        return
    
    print(f"\nStarting batch creation of {len(users_to_create)} users...")
    print("=" * 60)
    
    results = {
        'summary': {
            'total_attempted': len(users_to_create),
            'successful': 0,
            'failed': 0,
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'created_users': [],
        'failed_users': []
    }
    
    # Create each user account
    for i, user in enumerate(users_to_create, 1):
        print(f"\n[{i}/{len(users_to_create)}] Creating: {user['name']} {user['surname']}")
        print(f"Email: {user['email']}")
        
        result = create_user_account(user, script_path)
        
        user_result = {
            'name': user['name'],
            'surname': user['surname'],
            'email': user['email'],
            'success': result['success'],
            'return_code': result['return_code'],
            'status_info': result['status_info'],
            'stdout': result['stdout'][:500] + "..." if result['stdout'] and len(result['stdout']) > 500 else result['stdout'],  # Truncate long output
            'stderr': result['stderr'][:500] + "..." if result['stderr'] and len(result['stderr']) > 500 else result['stderr']   # Truncate long output
        }
        
        if 'error' in result:
            user_result['error'] = result['error']
        
        if result['success']:
            results['created_users'].append(user_result)
            results['summary']['successful'] += 1
            print(f"✓ SUCCESS: {user['name']} {user['surname']}")
            if result['status_info']:
                print(f"  Status: {result['status_info']}")
        else:
            results['failed_users'].append(user_result)
            results['summary']['failed'] += 1
            print(f"✗ FAILED: {user['name']} {user['surname']}")
            if result['status_info']:
                print(f"  Status: {result['status_info']}")
            if result['stderr']:
                print(f"  Error: {result['stderr'][:200]}...")
        
        # Add a small delay between requests to be nice to the server
        if i < len(users_to_create):  # Don't wait after the last user
            print(f"Waiting 2 seconds before next request...")
            time.sleep(2)
    
    # Finalize results
    results['summary']['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Save results
    save_creation_results(results)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("BATCH CREATION SUMMARY")
    print("=" * 60)
    print(f"Total attempted: {results['summary']['total_attempted']}")
    print(f"Successfully created: {results['summary']['successful']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Success rate: {results['summary']['successful'] / results['summary']['total_attempted'] * 100:.1f}%")
    
    if results['created_users']:
        print(f"\n✓ SUCCESSFULLY CREATED ({len(results['created_users'])}):")
        for user in results['created_users']:
            print(f"  - {user['name']} {user['surname']} ({user['email']})")
    
    if results['failed_users']:
        print(f"\n✗ FAILED TO CREATE ({len(results['failed_users'])}):")
        for user in results['failed_users']:
            print(f"  - {user['name']} {user['surname']} ({user['email']}) - {user['status_info']}")

if __name__ == "__main__":
    main() 