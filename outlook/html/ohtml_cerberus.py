import win32com.client as win32
from datetime import datetime, timedelta

def create_approval_email():
    """
    Create a Cerberus-enhanced Material Design approval email for chemical/material consumable
    """
    
    # Create Outlook application object
    outlook = win32.Dispatch('outlook.application')
    
    # Create a new mail item
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    
    # Email details
    mail.To = "manufacturing.team@company.com"
    mail.CC = "safety.department@company.com; procurement@company.com"
    mail.Subject = "✅ APPROVED: Chemical Consumable - Application 001/2025"
    
    # Calculate expiry date (example: 3 months from now)
    expiry_date = datetime.now() + timedelta(days=90)
    approval_date = datetime.now()
    
    # Cerberus-enhanced HTML email body
    html_body = f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="x-apple-disable-message-reformatting">
    <meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no">
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <title>Chemical Approval Notification - Application 001/2025</title>

    <!-- Outlook PixelsPerInch fix -->
    <!--[if gte mso 9]>
    <xml>
        <o:OfficeDocumentSettings>
            <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
    </xml>
    <![endif]-->

    <!-- Web Font Handling -->
    <!--[if mso]>
        <style>
            * {{
                font-family: Arial, sans-serif !important;
            }}
        </style>
    <![endif]-->

    <!--[if !mso]><!-->
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@300;400;500;600&display=swap');
    </style>
    <!--<![endif]-->

    <!-- CSS Reset & Enhancements -->
    <style>
        :root {{
            color-scheme: light dark;
            supported-color-schemes: light dark;
        }}

        html, body {{
            margin: 0 auto !important;
            padding: 0 !important;
            height: 100% !important;
            width: 100% !important;
        }}

        * {{
            -ms-text-size-adjust: 100%;
            -webkit-text-size-adjust: 100%;
        }}

        div[style*="margin: 16px 0"] {{
            margin: 0 !important;
        }}

        #MessageViewBody, #MessageWebViewDiv {{
            width: 100% !important;
        }}

        table, td {{
            mso-table-lspace: 0pt !important;
            mso-table-rspace: 0pt !important;
        }}

        table {{
            border-spacing: 0 !important;
            border-collapse: collapse !important;
            table-layout: fixed !important;
            margin: 0 auto !important;
        }}

        img {{
            -ms-interpolation-mode: bicubic;
        }}

        a {{
            text-decoration: none;
        }}

        /* Auto-detected links styling */
        a[x-apple-data-detectors],
        .unstyle-auto-detected-links a,
        .aBn {{
            border-bottom: 0 !important;
            cursor: default !important;
            color: inherit !important;
            text-decoration: none !important;
            font-size: inherit !important;
            font-family: inherit !important;
            font-weight: inherit !important;
            line-height: inherit !important;
        }}

        /* Gmail download button prevention */
        .a6S {{
            display: none !important;
            opacity: 0.01 !important;
        }}

        .im {{
            color: inherit !important;
        }}

        img.g-img + div {{
            display: none !important;
        }}

        /* Button hover effects */
        .button-td,
        .button-a {{
            transition: all 100ms ease-in;
        }}
        .button-td-primary:hover,
        .button-a-primary:hover {{
            background: #2e8b3e !important;
            border-color: #2e8b3e !important;
        }}

        /* Responsive adjustments */
        @media screen and (max-width: 680px) {{
            .email-container {{
                width: 100% !important;
                margin: auto !important;
            }}
            .fluid {{
                max-width: 100% !important !important;
                height: auto !important;
                margin-left: auto !important;
                margin-right: auto !important;
            }}
            .stack-column,
            .stack-column-center {{
                display: block !important;
                width: 100% !important;
                max-width: 100% !important;
                direction: ltr !important;
            }}
            .stack-column-center {{
                text-align: center !important;
            }}
            .center-on-narrow {{
                text-align: center !important;
                display: block !important;
                margin-left: auto !important;
                margin-right: auto !important;
                float: none !important;
            }}
            table.center-on-narrow {{
                display: inline-block !important;
            }}
        }}

        /* Dark Mode Support */
        @media (prefers-color-scheme: dark) {{
            .email-bg {{
                background: #1a1a1a !important;
            }}
            .darkmode-bg {{
                background: #2a2a2a !important;
            }}
            .darkmode-text {{
                color: #f0f0f0 !important;
            }}
            .darkmode-secondary {{
                color: #cccccc !important;
            }}
            td.button-td-primary,
            td.button-td-primary a {{
                background: #ffffff !important;
                border-color: #ffffff !important;
                color: #222222 !important;
            }}
            td.button-td-primary:hover,
            td.button-td-primary a:hover {{
                background: #cccccc !important;
                border-color: #cccccc !important;
            }}
        }}
    </style>
</head>

<body width="100%" style="margin: 0; padding: 0 !important; mso-line-height-rule: exactly; background-color: #f8f9fa;" class="email-bg">
    <center role="article" aria-roledescription="email" lang="en" style="width: 100%; background-color: #f8f9fa;" class="email-bg">
        <!--[if mso | IE]>
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8f9fa;">
        <tr>
        <td>
        <![endif]-->

        <!-- Preview Text -->
        <div style="max-height:0; overflow:hidden; mso-hide:all;" aria-hidden="true">
            Chemical approval notification for Tungsten Carbide Coating Solution WC-2024 - Application 001/2025 has been approved for use in Manufacturing Floor A, Bay 3-5.
        </div>
        
        <!-- Preview Text Spacing -->
        <div style="display: none; font-size: 1px; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all; font-family: sans-serif;">
            &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
        </div>

        <!-- Email Container -->
        <div style="max-width: 680px; margin: 0 auto;" class="email-container">
            <!--[if mso]>
            <table align="center" role="presentation" cellspacing="0" cellpadding="0" border="0" width="680">
            <tr>
            <td>
            <![endif]-->

            <!-- Email Body -->
            <table align="center" role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin: auto;">
                
                <!-- Header Section -->
                <tr>
                    <td style="background-color: #1a73e8; padding: 40px 20px;" class="darkmode-bg">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                            <tr>
                                <td style="text-align: left;">
                                    <h1 style="margin: 0; font-family: 'Google Sans', Arial, sans-serif; font-size: 28px; line-height: 34px; color: #ffffff; font-weight: 400;">Chemical Approval System</h1>
                                    <p style="margin: 8px 0 0 0; font-family: Arial, sans-serif; font-size: 16px; line-height: 20px; color: rgba(255,255,255,0.9);">Advanced Manufacturing Solutions</p>
                                </td>
                                <td class="stack-column-center" style="text-align: right;">
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="background-color: rgba(255,255,255,0.15); border-radius: 24px;">
                                        <tr>
                                            <td style="padding: 12px 20px; text-align: center;">
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #ffffff; font-weight: 500;">Application ID: <strong>001/2025</strong></p>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <!-- Product Card Section -->
                <tr>
                    <td style="background-color: #ffffff; padding: 40px 20px;" class="darkmode-bg">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #ffffff; border: 1px solid #e8eaed; border-radius: 12px;" class="darkmode-bg">
                            <tr>
                                <td style="padding: 32px;">
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <tr>
                                            <td class="stack-column" style="width: 65%; vertical-align: top;">
                                                <h2 style="margin: 0 0 20px 0; font-family: 'Google Sans', Arial, sans-serif; font-size: 24px; line-height: 30px; color: #202124; font-weight: 400;" class="darkmode-text">Tungsten Carbide Coating Solution WC-2024</h2>
                                                
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 20px;">
                                                    <tr>
                                                        <td style="padding: 6px 0; width: 140px;">
                                                            <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #5f6368; font-weight: 500;">Product Code:</p>
                                                        </td>
                                                        <td style="padding: 6px 0;">
                                                            <p style="margin: 0; font-family: 'Courier New', monospace; font-size: 14px; color: #202124;" class="darkmode-text">WC-2024-TC-500ML</p>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 6px 0;">
                                                            <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #5f6368; font-weight: 500;">Internal Code (TKZ):</p>
                                                        </td>
                                                        <td style="padding: 6px 0;">
                                                            <p style="margin: 0; font-family: 'Courier New', monospace; font-size: 14px; color: #202124;" class="darkmode-text">TKZ-2024-001</p>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 6px 0;">
                                                            <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #5f6368; font-weight: 500;">Application ID:</p>
                                                        </td>
                                                        <td style="padding: 6px 0;">
                                                            <p style="margin: 0; font-family: 'Courier New', monospace; font-size: 16px; color: #1a73e8; font-weight: 600;">001/2025</p>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 6px 0;">
                                                            <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #5f6368; font-weight: 500;">Product Class:</p>
                                                        </td>
                                                        <td style="padding: 6px 0;">
                                                            <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #202124;" class="darkmode-text">Industrial Coating Solution - Class II</p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                            <td class="stack-column-center" style="width: 35%; vertical-align: top; text-align: right;">
                                                <!-- Status Badges -->
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="right" class="center-on-narrow">
                                                    <tr>
                                                        <td style="padding: 0 0 12px 0;">
                                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="background-color: #34a853; border-radius: 24px; border: 2px solid #34a853;">
                                                                <tr>
                                                                    <td style="padding: 12px 20px; text-align: center;">
                                                                        <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #ffffff; font-weight: 500;">✓ APPROVED</p>
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td>
                                                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="background-color: #1a73e8; border-radius: 20px; border: 2px solid #1a73e8;">
                                                                <tr>
                                                                    <td style="padding: 8px 16px; text-align: center;">
                                                                        <p style="margin: 0; font-family: Arial, sans-serif; font-size: 12px; color: #ffffff; font-weight: 500;">🆕 FIRST USE</p>
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <!-- Main Content Section -->
                <tr>
                    <td style="background-color: #ffffff; padding: 0 20px 30px 20px;" class="darkmode-bg">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #ffffff; border-radius: 12px; border: 1px solid #f0f0f0;" class="darkmode-bg">
                            <tr>
                                <td style="padding: 32px;">
                                    <h3 style="margin: 0 0 20px 0; font-family: 'Google Sans', Arial, sans-serif; font-size: 20px; line-height: 26px; color: #202124; font-weight: 400;" class="darkmode-text">Laboratory Testing & Approval</h3>
                                    <p style="margin: 0 0 20px 0; font-family: Arial, sans-serif; font-size: 16px; line-height: 24px; color: #5f6368;" class="darkmode-secondary">This product has been thoroughly tested and approved by our specialized laboratories. All safety, environmental, and performance criteria have been met according to company standards and regulatory requirements.</p>
                                    
                                    <!-- Lab Badges -->
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 20px 0;">
                                        <tr>
                                            <td style="background-color: #e8f0fe; border-radius: 16px; border: 1px solid #e8f0fe;">
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                    <tr>
                                                        <td style="padding: 8px 16px;">
                                                            <p style="margin: 0; font-family: Arial, sans-serif; font-size: 13px; color: #1a73e8; font-weight: 500;">Health & Safety Lab</p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                            <td style="width: 12px;"></td>
                                            <td style="background-color: #e8f0fe; border-radius: 16px; border: 1px solid #e8f0fe;">
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                    <tr>
                                                        <td style="padding: 8px 16px;">
                                                            <p style="margin: 0; font-family: Arial, sans-serif; font-size: 13px; color: #1a73e8; font-weight: 500;">Environmental Testing</p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                            <td style="width: 12px;"></td>
                                            <td style="background-color: #e8f0fe; border-radius: 16px; border: 1px solid #e8f0fe;">
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                                    <tr>
                                                        <td style="padding: 8px 16px;">
                                                            <p style="margin: 0; font-family: Arial, sans-serif; font-size: 13px; color: #1a73e8; font-weight: 500;">Manufacturing Lab</p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Approval Details -->
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-top: 24px;">
                                        <tr>
                                            <td style="padding: 8px 0; width: 160px;">
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #5f6368; font-weight: 500;">Approval Date:</p>
                                            </td>
                                            <td style="padding: 8px 0;">
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #202124;" class="darkmode-text">{approval_date.strftime('%B %d, %Y')}</p>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0;">
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #5f6368; font-weight: 500;">Valid Until:</p>
                                            </td>
                                            <td style="padding: 8px 0;">
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #202124;" class="darkmode-text">{expiry_date.strftime('%B %d, %Y')}</p>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0;">
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #5f6368; font-weight: 500;">Approved Location:</p>
                                            </td>
                                            <td style="padding: 8px 0;">
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #202124;" class="darkmode-text">Manufacturing Floor A, Bay 3-5</p>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px 0;">
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #5f6368; font-weight: 500;">Usage Classification:</p>
                                            </td>
                                            <td style="padding: 8px 0;">
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; color: #202124;" class="darkmode-text">Controlled Industrial Use</p>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <!-- Links Section -->
                <tr>
                    <td style="background-color: #ffffff; padding: 0 20px 30px 20px;" class="darkmode-bg">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f8f9fa; border-left: 4px solid #34a853; border-radius: 12px;" class="darkmode-bg">
                            <tr>
                                <td style="padding: 32px;">
                                    <h3 style="margin: 0 0 16px 0; font-family: 'Google Sans', Arial, sans-serif; font-size: 18px; line-height: 24px; color: #202124; font-weight: 400;" class="darkmode-text">Documentation & Resources</h3>
                                    <p style="margin: 0 0 24px 0; font-family: Arial, sans-serif; font-size: 14px; color: #5f6368;" class="darkmode-secondary">Access complete documentation including application form, MSDS, TDS, and detailed specifications.</p>
                                    
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                        <tr>
                                            <td style="vertical-align: middle;">
                                                <!-- Primary Button (Cerberus Pattern) -->
                                                <table align="left" role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: auto;">
                                                    <tr>
                                                        <td class="button-td button-td-primary" style="border-radius: 8px; background: #34a853; border: 2px solid #34a853;">
                                                            <a class="button-a button-a-primary" href="https://normie.company.com/approvals/001-2025" style="background: #34a853; border: 2px solid #34a853; font-family: Arial, sans-serif; font-size: 14px; line-height: 14px; text-decoration: none; padding: 16px 24px; color: #ffffff; display: block; border-radius: 8px; font-weight: 500;">📋 Open in Normie Platform</a>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                            <td style="width: 24px;"></td>
                                            <td style="vertical-align: middle;">
                                                <a href="https://legacy.company.com/approvals/001-2025" style="color: #1a73e8; text-decoration: underline; font-family: Arial, sans-serif; font-size: 14px; font-weight: 400;">Legacy System Access</a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <!-- Warning Section -->
                <tr>
                    <td style="background-color: #ffffff; padding: 0 20px 40px 20px;" class="darkmode-bg">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #fef7e0; border: 2px solid #f9ab00; border-left: 4px solid #ea4335; border-radius: 12px;">
                            <tr>
                                <td style="padding: 32px;">
                                    <h3 style="margin: 0 0 20px 0; font-family: 'Google Sans', Arial, sans-serif; font-size: 20px; line-height: 26px; color: #d93025; font-weight: 500;">⚠️ Critical Approval Conditions</h3>
                                    
                                    <!-- Warning Item 1 -->
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 16px;">
                                        <tr>
                                            <td style="background-color: #ffffff; padding: 20px; border-radius: 8px; border-left: 4px solid #ea4335; border: 1px solid #f0f0f0;">
                                                <p style="margin: 0 0 8px 0; font-family: Arial, sans-serif; font-size: 16px; color: #d93025; font-weight: 600;">Expiry Date Compliance</p>
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; color: #5f6368;">Product usage cannot exceed 1/4 of the remaining time until expiry date. Current product expires on {(expiry_date + timedelta(days=120)).strftime('%B %d, %Y')}. Monitor usage carefully.</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Warning Item 2 -->
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin-bottom: 16px;">
                                        <tr>
                                            <td style="background-color: #ffffff; padding: 20px; border-radius: 8px; border-left: 4px solid #ea4335; border: 1px solid #f0f0f0;">
                                                <p style="margin: 0 0 8px 0; font-family: Arial, sans-serif; font-size: 16px; color: #d93025; font-weight: 600;">Specification Certification Required</p>
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; color: #5f6368;">Product must be certified to meet all technical specifications as outlined in the Technical Data Sheet before use. No exceptions permitted.</p>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Warning Item 3 -->
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <tr>
                                            <td style="background-color: #ffffff; padding: 20px; border-radius: 8px; border-left: 4px solid #ea4335; border: 1px solid #f0f0f0;">
                                                <p style="margin: 0 0 8px 0; font-family: Arial, sans-serif; font-size: 16px; color: #d93025; font-weight: 600;">Mandatory Usage Monitoring</p>
                                                <p style="margin: 0; font-family: Arial, sans-serif; font-size: 14px; line-height: 20px; color: #5f6368;">All usage must be logged and reported according to safety protocols. Real-time monitoring required for compliance.</p>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>

                <!-- Spacer -->
                <tr>
                    <td aria-hidden="true" height="20" style="font-size: 0px; line-height: 0px;">
                        &nbsp;
                    </td>
                </tr>

            </table>
            <!-- Email Body : END -->

            <!-- Footer -->
            <table align="center" role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin: auto;">
                <tr>
                    <td style="padding: 32px 20px; font-family: Arial, sans-serif; font-size: 13px; line-height: 18px; text-align: center; color: #5f6368; background-color: #f8f9fa; border-top: 1px solid #e8eaed;" class="darkmode-bg darkmode-secondary">
                        <strong style="color: #202124;" class="darkmode-text">Quality Assurance & Safety Department</strong><br>
                        Advanced Manufacturing Solutions<br>
                        <span class="unstyle-auto-detected-links">Phone: +1 (555) 123-4567 | Email: safety@company.com</span><br><br>
                        <em>This is an automated approval notification generated on {approval_date.strftime('%B %d, %Y at %I:%M %p')}</em><br>
                        <strong>Confidential:</strong> This approval is specific to the conditions stated above. Any deviation requires re-evaluation.
                    </td>
                </tr>
            </table>

            <!--[if mso]>
            </td>
            </tr>
            </table>
            <![endif]-->
        </div>

        <!--[if mso | IE]>
        </td>
        </tr>
        </table>
        <![endif]-->
    </center>
</body>
</html>"""
    
    # Set the HTML body
    mail.HTMLBody = html_body
    
    # Display the email instead of sending it
    mail.Display(True)
    
    print("🎉 Cerberus-Enhanced Material Design Email Created!")
    print(f"📧 Subject: {mail.Subject}")
    print(f"📧 To: {mail.To}")
    print(f"📧 CC: {mail.CC}")
    print("\n🛡️ Cerberus Enhancements Applied:")
    print("• Full DOCTYPE and meta tag optimization")
    print("• Outlook PixelsPerInch fix")
    print("• Web font conditional loading")
    print("• Comprehensive CSS reset")
    print("• Auto-detected links styling")
    print("• Gmail download button prevention")
    print("• Button hover effects")
    print("• Responsive design with stack columns")
    print("• Dark mode support")
    print("• Preview text optimization")
    print("• MSO conditional comments")
    print("• Proper role and aria attributes")
    print("• Border fallbacks for shadows")
    print("• Professional Cerberus button pattern")
    print("\n✨ This email will render perfectly across all major email clients!")

if __name__ == "__main__":
    try:
        create_approval_email()
    except Exception as e:
        print(f"❌ Error creating email: {str(e)}")
        print("💡 Make sure Microsoft Outlook is installed and accessible via COM.") 