import json
import csv
import subprocess
import sys
import time
import os
from pathlib import Path

def load_user_ids_from_file(file_path):
    """Load user IDs from various file formats"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist!")
        return []
    
    user_ids = []
    
    try:
        if file_path.suffix.lower() == '.json':
            # Load from JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                # List of user IDs or user objects
                for item in data:
                    if isinstance(item, int):
                        user_ids.append(item)
                    elif isinstance(item, dict):
                        # Look for common ID fields
                        for id_field in ['id', 'user_id', 'userId', 'entityId']:
                            if id_field in item:
                                user_ids.append(int(item[id_field]))
                                break
            elif isinstance(data, dict):
                # Dictionary with user IDs
                if 'user_ids' in data:
                    user_ids = [int(uid) for uid in data['user_ids']]
                elif 'users' in data:
                    for user in data['users']:
                        if isinstance(user, dict):
                            for id_field in ['id', 'user_id', 'userId', 'entityId']:
                                if id_field in user:
                                    user_ids.append(int(user[id_field]))
                                    break
        
        elif file_path.suffix.lower() == '.csv':
            # Load from CSV file
            with open(file_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    # Look for ID column
                    for id_field in ['id', 'user_id', 'userId', 'entityId', 'ID', 'User_ID']:
                        if id_field in row:
                            user_ids.append(int(row[id_field]))
                            break
        
        elif file_path.suffix.lower() == '.txt':
            # Load from text file (one ID per line)
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.isdigit():
                        user_ids.append(int(line))
        
        else:
            print(f"Unsupported file format: {file_path.suffix}")
            return []
    
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return []
    
    return user_ids

def reset_password_single_user(user_id, script_path='pwreset.ps1'):
    """Reset password for a single user using PowerShell script"""
    try:
        # Execute the PowerShell script with user ID parameter
        result = subprocess.run([
            'powershell.exe', 
            '-ExecutionPolicy', 'Bypass',
            '-File', script_path,
            '-UserId', str(user_id)
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
            'user_id': user_id,
            'success': success,
            'return_code': result.returncode,
            'stdout': stdout_content,
            'stderr': stderr_content,
            'status_info': status_info
        }
        
    except Exception as e:
        return {
            'user_id': user_id,
            'success': False,
            'return_code': -1,
            'stdout': None,
            'stderr': None,
            'error': str(e),
            'status_info': f"Exception: {str(e)}"
        }

def save_reset_results(results, output_file='password_reset_results.json'):
    """Save the password reset results to a JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Reset results saved to: {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    """Main function to handle password resets"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single user:     python pwreset.py <user_id>")
        print("  From file:       python pwreset.py <file_path>")
        print("  Examples:")
        print("    python pwreset.py 360")
        print("    python pwreset.py user_ids.json")
        print("    python pwreset.py user_ids.csv")
        print("    python pwreset.py user_ids.txt")
        return
    
    input_arg = sys.argv[1]
    
    # Determine if input is a user ID or file path
    user_ids = []
    
    if input_arg.isdigit():
        # Single user ID
        user_ids = [int(input_arg)]
        print(f"Resetting password for user ID: {input_arg}")
    else:
        # File path
        print(f"Loading user IDs from file: {input_arg}")
        user_ids = load_user_ids_from_file(input_arg)
        
        if not user_ids:
            print("No valid user IDs found in file!")
            return
        
        print(f"Found {len(user_ids)} user IDs to process:")
        for uid in user_ids:
            print(f"  - User ID: {uid}")
    
    # Ask for confirmation for batch operations
    if len(user_ids) > 1:
        response = input(f"\nDo you want to reset passwords for {len(user_ids)} users? (y/N): ")
        if response.lower() != 'y':
            print("Password reset cancelled.")
            return
    
    # Check if PowerShell script exists
    script_path = 'pwreset.ps1'
    if not os.path.exists(script_path):
        print(f"PowerShell script {script_path} not found!")
        return
    
    print(f"\nStarting password reset for {len(user_ids)} user(s)...")
    print("=" * 60)
    
    results = {
        'summary': {
            'total_attempted': len(user_ids),
            'successful': 0,
            'failed': 0,
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'successful_resets': [],
        'failed_resets': []
    }
    
    # Process each user ID
    for i, user_id in enumerate(user_ids, 1):
        print(f"\n[{i}/{len(user_ids)}] Resetting password for user ID: {user_id}")
        
        result = reset_password_single_user(user_id, script_path)
        
        user_result = {
            'user_id': user_id,
            'success': result['success'],
            'return_code': result['return_code'],
            'status_info': result['status_info'],
            'stdout': result['stdout'][:500] + "..." if result['stdout'] and len(result['stdout']) > 500 else result['stdout'],  # Truncate long output
            'stderr': result['stderr'][:500] + "..." if result['stderr'] and len(result['stderr']) > 500 else result['stderr']   # Truncate long output
        }
        
        if 'error' in result:
            user_result['error'] = result['error']
        
        if result['success']:
            results['successful_resets'].append(user_result)
            results['summary']['successful'] += 1
            print(f"✓ SUCCESS: User ID {user_id}")
            if result['status_info']:
                print(f"  Status: {result['status_info']}")
        else:
            results['failed_resets'].append(user_result)
            results['summary']['failed'] += 1
            print(f"✗ FAILED: User ID {user_id}")
            if result['status_info']:
                print(f"  Status: {result['status_info']}")
            if result['stderr']:
                print(f"  Error: {result['stderr'][:200]}...")
        
        # Add a small delay between requests for batch operations
        if len(user_ids) > 1 and i < len(user_ids):
            print(f"Waiting 2 seconds before next request...")
            time.sleep(2)
    
    # Finalize results
    results['summary']['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Save results
    save_reset_results(results)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("PASSWORD RESET SUMMARY")
    print("=" * 60)
    print(f"Total attempted: {results['summary']['total_attempted']}")
    print(f"Successfully reset: {results['summary']['successful']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Success rate: {results['summary']['successful'] / results['summary']['total_attempted'] * 100:.1f}%")
    
    if results['successful_resets']:
        print(f"\n✓ SUCCESSFULLY RESET ({len(results['successful_resets'])}):")
        for reset in results['successful_resets']:
            print(f"  - User ID: {reset['user_id']}")
    
    if results['failed_resets']:
        print(f"\n✗ FAILED TO RESET ({len(results['failed_resets'])}):")
        for reset in results['failed_resets']:
            print(f"  - User ID: {reset['user_id']} - {reset['status_info']}")

if __name__ == "__main__":
    main()
