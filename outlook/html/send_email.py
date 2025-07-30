import win32com.client as win32
import os

def send_approval_email():
    """
    Send approval email using HTML file directly
    """
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_dir, "cerberus-fluid.html")
    
    # Read HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
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
    print("✅ Email loaded from file and ready to send!")

if __name__ == "__main__":
    send_approval_email() 