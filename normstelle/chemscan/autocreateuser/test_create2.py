import subprocess
import sys

def test_create_user(name, surname, email):
    """Test creating one user account with create2.ps1"""
    script_path = 'create2.ps1'
    
    print(f"Testing user creation with create2.ps1 for: {name} {surname} ({email})")
    print("-" * 60)
    
    try:
        # Execute the PowerShell script with user parameters
        # Use different encoding strategies to handle special characters
        result = subprocess.run([
            'powershell.exe', 
            '-ExecutionPolicy', 'Bypass',
            '-File', script_path,
            '-Name', name,
            '-Surname', surname,
            '-Email', email
        ], capture_output=True, text=False)  # Get bytes instead of text initially
        
        print(f"Return Code: {result.returncode}")
        
        # Try to decode stdout with multiple encoding strategies
        stdout_content = ""
        if result.stdout:
            try:
                stdout_content = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    stdout_content = result.stdout.decode('cp1252')  # Windows encoding
                except UnicodeDecodeError:
                    try:
                        stdout_content = result.stdout.decode('utf-8', errors='replace')
                    except:
                        stdout_content = str(result.stdout)
        
        # Try to decode stderr with multiple encoding strategies
        stderr_content = ""
        if result.stderr:
            try:
                stderr_content = result.stderr.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    stderr_content = result.stderr.decode('cp1252')  # Windows encoding
                except UnicodeDecodeError:
                    try:
                        stderr_content = result.stderr.decode('utf-8', errors='replace')
                    except:
                        stderr_content = str(result.stderr)
        
        print(f"STDOUT:\n{stdout_content}")
        
        if stderr_content:
            print(f"STDERR:\n{stderr_content}")
        
        if result.returncode == 0:
            print("✓ User creation appears successful!")
            
            # Try to extract useful information from the response
            if "StatusCode" in stdout_content:
                if "200" in stdout_content:
                    print("✓ HTTP 200 - Request successful!")
                elif "400" in stdout_content:
                    print("⚠ HTTP 400 - Bad Request (check data)")
                elif "401" in stdout_content:
                    print("⚠ HTTP 401 - Authentication failed")
                elif "403" in stdout_content:
                    print("⚠ HTTP 403 - Forbidden")
                elif "500" in stdout_content:
                    print("⚠ HTTP 500 - Server Error")
            
            if "error" in stdout_content.lower() or "exception" in stdout_content.lower():
                print("⚠ Response contains error/exception messages")
                
        else:
            print("✗ User creation failed!")
            
    except Exception as e:
        print(f"Error executing PowerShell script: {e}")

def main():
    """Main function - can be called with arguments or use default test user"""
    
    if len(sys.argv) == 4:
        # Use command line arguments
        name = sys.argv[1]
        surname = sys.argv[2] 
        email = sys.argv[3]
    else:
        # Use a test user with umlauts
        print("No arguments provided. Using test user with umlauts...")
        print("Usage: python test_create2.py <name> <surname> <email>")
        print()
        
        # Test with German umlauts to verify proper handling
        name = "Björn"
        surname = "Müller"
        email = "bjoern.mueller@test.com"
        
        print(f"Using test data with umlauts: {name} {surname} ({email})")
        response = input("Continue with test user? (y/N): ")
        if response.lower() != 'y':
            print("Test cancelled.")
            return
    
    test_create_user(name, surname, email)

if __name__ == "__main__":
    main() 