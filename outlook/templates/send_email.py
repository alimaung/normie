import win32com.client as win32
import os
import argparse

def send_approval_email(file_name="cerberus-fluid.html"):
    """
    Send approval email using HTML file directly
    
    Args:
        file_name (str): Name of the HTML file to use for email content
    """
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_dir, file_name)
    
    # Check if file exists
    if not os.path.exists(html_file):
        print(f"❌ Error: File '{file_name}' not found in {current_dir}")
        return
    
    # Read HTML file
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"❌ Error reading file '{file_name}': {e}")
        return
    
    # Create Outlook mail
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    
    # Set email details
    mail.To = "manufacturing.team@company.com"
    mail.CC = "safety.department@company.com; procurement@company.com"
    mail.Subject = "✅ APPROVED: Chemical Consumable - Application 001/2025"
    mail.HTMLBody = html_content
    
    # Display email
    mail.Display(True)
    print(f"✅ Email loaded from '{file_name}' and ready to send!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send approval email using specified HTML template')
    parser.add_argument('--file', '-f', 
                       default='cerberus-fluid.html',
                       help='HTML file to use for email content (default: cerberus-fluid.html)')
    
    args = parser.parse_args()
    send_approval_email(args.file) 