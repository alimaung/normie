import json
import subprocess
import os
from urllib.parse import quote

def load_user_list():
    """Load the list of users from list.json"""
    with open('list.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def execute_powershell_script_with_param(surname, script_path):
    """Execute the PowerShell script with the surname as a parameter"""
    try:
        # Execute the PowerShell script with the name parameter
        result = subprocess.run([
            'powershell.exe', 
            '-ExecutionPolicy', 'Bypass',
            '-File', script_path,
            '-Name', surname
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"PowerShell script failed with error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error executing PowerShell script: {e}")
        return None

def save_response(surname, response_content):
    """Save the response to a file in the users directory"""
    # Create users directory if it doesn't exist
    users_dir = 'users'
    if not os.path.exists(users_dir):
        os.makedirs(users_dir)
    
    # Save the response with surname as filename
    filename = f"{surname.replace(' ', '_').replace('/', '_').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')}.html"
    filepath = os.path.join(users_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(response_content)
    
    print(f"Saved response for {surname} to {filepath}")

def main():
    """Main function to process all users"""
    print("Loading user list...")
    users = load_user_list()
    
    print(f"Found {len(users)} users to process")
    
    script_path = 'request.ps1'
    
    for i, user in enumerate(users, 1):
        surname = user['surname']
        name = user['name']
        email = user['email']
        
        print(f"Processing {i}/{len(users)}: {name} {surname} ({email})")
        
        # Execute the script with the surname as parameter
        response = execute_powershell_script_with_param(surname, script_path)
        
        if response:
            # Save the response
            save_response(surname, response)
        else:
            print(f"Failed to get response for {surname}")
        
        print(f"Completed processing for {surname}")
        print("-" * 50)

if __name__ == "__main__":
    main()


