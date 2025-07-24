import json
from pathlib import Path

def load_existing_users(analysis_file='user_analysis_results_simple.json'):
    """Load the list of existing users from the analysis results"""
    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('existing_users', [])
    except Exception as e:
        print(f"Error loading analysis file {analysis_file}: {e}")
        return []

def load_parsed_users(parsed_file='parsed_users.json'):
    """Load the detailed user data from the parsed users database"""
    try:
        with open(parsed_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading parsed users file {parsed_file}: {e}")
        return []

def find_user_in_database(user_email, parsed_users):
    """Find a user in the parsed users database by email"""
    for user in parsed_users:
        if user.get('email', '').lower() == user_email.lower():
            return user
    return None

def determine_reset_needed(user_data):
    """Determine if a user needs a password reset based on their status and login history"""
    if not user_data:
        return False, "User not found in database"
    
    status_active = user_data.get('status_active', False)
    last_login = user_data.get('last_login', '')
    
    # Check if last_login indicates never logged in
    never_logged_in = (
        last_login is None or 
        last_login == '' or 
        'Nicht verfügbar' in str(last_login) or 
        'Not available' in str(last_login)
    )
    
    if not status_active:
        return False, "Account not active"
    elif status_active and never_logged_in:
        return True, "Active account, never logged in"
    elif status_active and not never_logged_in:
        return False, "Active account, has logged in"
    else:
        return False, "Unknown status"

def analyze_reset_requirements():
    """Main analysis function to determine which users need password resets"""
    print("Loading existing users...")
    existing_users = load_existing_users()
    
    if not existing_users:
        print("No existing users found!")
        return []
    
    print(f"Found {len(existing_users)} existing users")
    
    print("Loading parsed user database...")
    parsed_users = load_parsed_users()
    
    if not parsed_users:
        print("No parsed user data found!")
        return []
    
    print(f"Found {len(parsed_users)} users in database")
    
    reset_needed = []
    reset_not_needed = []
    not_found = []
    
    print("\nAnalyzing reset requirements...")
    print("=" * 60)
    
    for user in existing_users:
        name = user.get('name', '')
        surname = user.get('surname', '')
        email = user.get('email', '')
        
        print(f"Checking: {name} {surname} ({email})")
        
        # Find user in database
        user_data = find_user_in_database(email, parsed_users)
        
        if not user_data:
            not_found.append({
                'name': name,
                'surname': surname,
                'email': email,
                'reason': 'Not found in database'
            })
            print(f"  ⚠ Not found in database")
            continue
        
        # Determine if reset is needed
        needs_reset, reason = determine_reset_needed(user_data)
        
        user_info = {
            'name': name,
            'surname': surname,
            'email': email,
            'user_id': user_data.get('user_id'),
            'status_active': user_data.get('status_active'),
            'last_login': user_data.get('last_login'),
            'reason': reason
        }
        
        if needs_reset:
            reset_needed.append(user_info)
            print(f"  🔄 RESET NEEDED: {reason}")
        else:
            reset_not_needed.append(user_info)
            print(f"  ✓ No reset needed: {reason}")
    
    return reset_needed, reset_not_needed, not_found

def save_reset_analysis(reset_needed, reset_not_needed, not_found, output_file='password_reset_analysis.json'):
    """Save the analysis results to JSON file"""
    results = {
        'summary': {
            'total_analyzed': len(reset_needed) + len(reset_not_needed) + len(not_found),
            'reset_needed_count': len(reset_needed),
            'reset_not_needed_count': len(reset_not_needed),
            'not_found_count': len(not_found)
        },
        'users_needing_reset': reset_needed,
        'users_not_needing_reset': reset_not_needed,
        'users_not_found': not_found
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nAnalysis results saved to: {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

def save_reset_list_for_pwreset(reset_needed, output_file='users_need_reset.json'):
    """Save a simple list of user IDs that need reset for use with pwreset.py"""
    # Extract user IDs for users that need reset
    user_ids = []
    for user in reset_needed:
        user_id = user.get('user_id')
        if user_id:
            user_ids.append(user_id)
    
    # Save in format compatible with pwreset.py
    reset_data = {
        'user_ids': user_ids,
        'users': reset_needed
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(reset_data, f, indent=2, ensure_ascii=False)
        print(f"Reset list saved to: {output_file}")
        print(f"Use with: python pwreset.py {output_file}")
    except Exception as e:
        print(f"Error saving reset list: {e}")

def main():
    """Main function to analyze and report password reset requirements"""
    print("Password Reset Analysis")
    print("=" * 60)
    
    # Perform analysis
    reset_needed, reset_not_needed, not_found = analyze_reset_requirements()
    
    # Save detailed analysis
    save_reset_analysis(reset_needed, reset_not_needed, not_found)
    
    # Save simple reset list for pwreset.py
    if reset_needed:
        save_reset_list_for_pwreset(reset_needed)
    
    # Print summary
    print("\n" + "=" * 60)
    print("PASSWORD RESET ANALYSIS SUMMARY")
    print("=" * 60)
    
    total = len(reset_needed) + len(reset_not_needed) + len(not_found)
    print(f"Total users analyzed: {total}")
    print(f"Users needing reset: {len(reset_needed)}")
    print(f"Users not needing reset: {len(reset_not_needed)}")
    print(f"Users not found in database: {len(not_found)}")
    
    if reset_needed:
        print(f"\n🔄 USERS NEEDING PASSWORD RESET ({len(reset_needed)}):")
        for user in reset_needed:
            print(f"  - {user['name']} {user['surname']} ({user['email']}) - ID: {user.get('user_id', 'N/A')}")
            print(f"    Reason: {user['reason']}")
            print(f"    Status: Active={user.get('status_active')}, Last Login={user.get('last_login', 'N/A')}")
    
    if reset_not_needed:
        print(f"\n✓ USERS NOT NEEDING RESET ({len(reset_not_needed)}):")
        for user in reset_not_needed:
            print(f"  - {user['name']} {user['surname']} ({user['email']}) - ID: {user.get('user_id', 'N/A')}")
            print(f"    Reason: {user['reason']}")
    
    if not_found:
        print(f"\n⚠ USERS NOT FOUND IN DATABASE ({len(not_found)}):")
        for user in not_found:
            print(f"  - {user['name']} {user['surname']} ({user['email']})")
    
    if reset_needed:
        print(f"\n🔧 NEXT STEPS:")
        print(f"  1. Review the analysis results in 'password_reset_analysis.json'")
        print(f"  2. Run password resets: python pwreset.py users_need_reset.json")
        print(f"  3. This will reset passwords for {len(reset_needed)} users")

if __name__ == "__main__":
    main()
