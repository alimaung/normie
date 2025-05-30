
import win32com.client as com
try:
    outlook = com.Dispatch("Outlook.Application")

    """
    Source - https://msdn.microsoft.com/en-us/library/office/ff869291.aspx
    Outlook VBA Reference 
    0 - olMailItem
    1 - olAppointmentItem
    2 - olContactItem
    3 - olTaskItem
    4 - olJournalItem
    5 - olNoteItem 
    6 - olPostItem
    7 - olDistributionListItem
    """
    # mail = outlook.CreateItem(0X0) # 0X0 is the default value for the mail item
    mail = outlook.CreateItem(0)

    mail.To = "ali.maung002@gmail.com"

    #mail.CC = "mail2@example.com"

    #mail.BCC = "mail3@example.com"

    mail.Subject = "Test mail from Python"

    # Using "Body" constructs body as plain text
    # mail.Body = "Test mail body from Python"

    """
    Using "HtmlBody" constructs body as html text
    default font size for most browser is 12
    setting font size to "-1" might set it to 10
    """
    mail.HTMLBody = """
    <html>
    <head></head>
    <body>
    <font color="Blue" size=-1 face="Arial">
    <p>Hi!<br>
        HELLO THERE!<br>
        Test HTML mail body from Python
        <div style="color: red; font-size: 12px;">
            This is a div with red text and 12px font size.
        </div>
        <div style="color: green; font-size: 14px;">
            This is a div with green text and 14px font size.
        </div>
    </p>
    </font>
    </body>
    </html>
    """

    """
    Set the format of mail
    1 - Plain Text
    2 - HTML
    3 - Rich Text
    """
    mail.BodyFormat = 2


    # Instead of sending the message, just display the compiled message
    # Useful for visual inspection of compiled message
    #mail.Display(True)

    # Send the mail
    # Use this directly if there is no need for visual inspection
    mail.Send()
    print("Mail sent successfully.")
    input("Press Enter to continue...")
except Exception as e:
    print(f"An error occurred: {e}")
    print("Mail not sent.")
    input("Press Enter to continue...")
