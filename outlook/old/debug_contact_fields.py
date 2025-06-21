import win32com.client
import json
from collections import defaultdict, Counter
from datetime import datetime


class ContactFieldDebugger:
    """
    A comprehensive debugger to analyze all available fields/properties 
    on Outlook contact objects.
    """
    
    def __init__(self):
        self.outlook = None
        self.namespace = None
        self.all_properties = set()
        self.property_values = defaultdict(list)
        self.property_errors = defaultdict(list)
        self.property_types = defaultdict(set)
        
    def connect_to_outlook(self) -> bool:
        """Connect to Outlook application."""
        try:
            print("🔗 Connecting to Outlook...")
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            print("✅ Connected successfully!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_all_contact_properties(self, contact):
        """
        Attempt to discover all available properties on a contact object.
        Uses multiple methods to find properties.
        """
        properties_found = {}
        
        # Method 1: Try common Outlook contact properties
        common_properties = [
            # Basic Info
            'FullName', 'FirstName', 'LastName', 'MiddleName', 'Title', 'Suffix',
            'NickName', 'CompanyName', 'JobTitle', 'Department', 'OfficeLocation',
            'Profession', 'AssistantName', 'ManagerName',
            
            # Email addresses
            'Email1Address', 'Email2Address', 'Email3Address',
            'Email1AddressType', 'Email2AddressType', 'Email3AddressType',
            'Email1DisplayName', 'Email2DisplayName', 'Email3DisplayName',
            'EmailAddress', 'PrimarySmtpAddress',
            
            # Phone numbers
            'BusinessTelephoneNumber', 'HomeTelephoneNumber', 'MobileTelephoneNumber',
            'BusinessFaxNumber', 'HomeFaxNumber', 'PagerNumber', 'CarTelephoneNumber',
            'OtherTelephoneNumber', 'PrimaryTelephoneNumber', 'RadioTelephoneNumber',
            'CallbackTelephoneNumber', 'TTYTDDTelephoneNumber', 'Business2TelephoneNumber',
            'Home2TelephoneNumber', 'ISDNNumber', 'TelexNumber',
            
            # Addresses
            'BusinessAddress', 'HomeAddress', 'OtherAddress',
            'BusinessAddressStreet', 'BusinessAddressCity', 'BusinessAddressState',
            'BusinessAddressPostalCode', 'BusinessAddressCountry',
            'HomeAddressStreet', 'HomeAddressCity', 'HomeAddressState',
            'HomeAddressPostalCode', 'HomeAddressCountry',
            'OtherAddressStreet', 'OtherAddressCity', 'OtherAddressState',
            'OtherAddressPostalCode', 'OtherAddressCountry',
            'SelectedMailingAddress',
            
            # Web and social
            'WebPage', 'BusinessHomePage', 'PersonalHomePage', 'FTPSite',
            'NetMeetingServer', 'NetMeetingAlias',
            
            # Personal info
            'Birthday', 'Anniversary', 'Spouse', 'Children', 'Gender',
            'Hobby', 'Language', 'Location', 'OrganizationalIDNumber',
            
            # Categories and notes
            'Categories', 'Body', 'Subject', 'Sensitivity', 'Importance',
            
            # System fields
            'Class', 'MessageClass', 'CreationTime', 'LastModificationTime',
            'Size', 'UnRead', 'EntryID', 'ConversationID',
            
            # Custom fields
            'User1', 'User2', 'User3', 'User4',
            'UserField1', 'UserField2', 'UserField3', 'UserField4',
            
            # Additional fields
            'Account', 'BillingInformation', 'Mileage', 'NoAging',
            'OutlookInternalVersion', 'OutlookVersion'
        ]
        
        # Test each property
        for prop in common_properties:
            try:
                if hasattr(contact, prop):
                    try:
                        value = getattr(contact, prop, None)
                        properties_found[prop] = {
                            'value': value,
                            'type': type(value).__name__,
                            'has_value': value is not None and str(value).strip() != '',
                            'string_value': str(value) if value is not None else None
                        }
                        self.all_properties.add(prop)
                        if value is not None:
                            self.property_types[prop].add(type(value).__name__)
                            if str(value).strip():
                                self.property_values[prop].append(str(value)[:100])  # Limit length
                    except Exception as access_error:
                        properties_found[prop] = {
                            'error': f'Access error: {access_error}',
                            'has_property': True,
                            'can_access': False
                        }
                        self.property_errors[prop].append(str(access_error))
                else:
                    properties_found[prop] = {
                        'has_property': False
                    }
            except Exception as e:
                properties_found[prop] = {
                    'error': f'Check error: {e}',
                    'has_property': False
                }
        
        # Method 2: Try to use COM object introspection (if available)
        try:
            # Some COM objects support _oleobj_ for introspection
            if hasattr(contact, '_oleobj_'):
                print(f"  📋 COM object type: {type(contact._oleobj_)}")
        except:
            pass
        
        return properties_found
    
    def analyze_contacts(self, max_contacts: int = 100):
        """
        Analyze the first N contacts and gather comprehensive field information.
        """
        if not self.connect_to_outlook():
            return None
        
        try:
            # Get contacts folder
            contacts_folder = self.namespace.GetDefaultFolder(10)  # olFolderContacts
            items = contacts_folder.Items
            total_items = items.Count
            
            print(f"📁 Analyzing contacts in folder: {contacts_folder.Name}")
            print(f"📊 Total items in folder: {total_items}")
            print(f"🔍 Will analyze up to {max_contacts} contacts")
            print("=" * 60)
            
            contact_analyses = []
            contacts_processed = 0
            
            for i, item in enumerate(items):
                if contacts_processed >= max_contacts:
                    break
                    
                try:
                    # Check if it's a contact
                    if hasattr(item, 'Class') and item.Class == 40:  # olContact
                        contacts_processed += 1
                        
                        print(f"\n🔍 Analyzing Contact #{contacts_processed}")
                        
                        # Get basic identification
                        name = "Unknown"
                        try:
                            name = getattr(item, 'FullName', 'No FullName')
                            if not name:
                                name = f"{getattr(item, 'FirstName', '')} {getattr(item, 'LastName', '')}".strip()
                            if not name:
                                name = f"Contact #{contacts_processed}"
                        except:
                            name = f"Contact #{contacts_processed}"
                        
                        print(f"   Name: {name}")
                        
                        # Analyze all properties
                        properties = self.get_all_contact_properties(item)
                        
                        contact_analysis = {
                            'contact_number': contacts_processed,
                            'name': name,
                            'properties': properties,
                            'total_properties_found': len([p for p in properties.values() if p.get('has_property', False)]),
                            'properties_with_values': len([p for p in properties.values() if p.get('has_value', False)])
                        }
                        
                        contact_analyses.append(contact_analysis)
                        
                        # Show progress
                        if contacts_processed % 10 == 0:
                            print(f"   ✅ Progress: {contacts_processed}/{max_contacts} contacts analyzed")
                        
                except Exception as e:
                    print(f"   ❌ Error analyzing item {i+1}: {e}")
                    continue
            
            print(f"\n🎉 Analysis complete! Processed {contacts_processed} contacts")
            return contact_analyses
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return None
    
    def generate_summary_report(self, contact_analyses):
        """Generate a comprehensive summary report."""
        if not contact_analyses:
            print("❌ No contact analyses to summarize")
            return
        
        print("\n" + "="*80)
        print("📋 COMPREHENSIVE FIELD ANALYSIS REPORT")
        print("="*80)
        
        # Overall statistics
        total_contacts = len(contact_analyses)
        print(f"\n📊 Overall Statistics:")
        print(f"   • Total contacts analyzed: {total_contacts}")
        print(f"   • Total unique properties discovered: {len(self.all_properties)}")
        
        # Property availability analysis
        property_availability = Counter()
        property_with_values = Counter()
        
        for analysis in contact_analyses:
            for prop_name, prop_data in analysis['properties'].items():
                if prop_data.get('has_property', False):
                    property_availability[prop_name] += 1
                if prop_data.get('has_value', False):
                    property_with_values[prop_name] += 1
        
        print(f"\n🔍 Most Common Properties (available in contacts):")
        for prop, count in property_availability.most_common(20):
            percentage = (count / total_contacts) * 100
            print(f"   • {prop}: {count}/{total_contacts} ({percentage:.1f}%)")
        
        print(f"\n✅ Properties with Actual Values (non-empty):")
        for prop, count in property_with_values.most_common(20):
            percentage = (count / total_contacts) * 100
            print(f"   • {prop}: {count}/{total_contacts} ({percentage:.1f}%)")
        
        # Email field analysis
        print(f"\n📧 Email Field Analysis:")
        email_fields = [prop for prop in self.all_properties if 'email' in prop.lower() or 'smtp' in prop.lower()]
        for field in sorted(email_fields):
            available = property_availability.get(field, 0)
            with_values = property_with_values.get(field, 0)
            print(f"   • {field}: Available in {available} contacts, {with_values} have values")
        
        # Error analysis
        print(f"\n⚠️ Property Access Errors:")
        for prop, errors in self.property_errors.items():
            if errors:
                print(f"   • {prop}: {len(errors)} errors")
                # Show unique error types
                unique_errors = list(set(errors))
                for error in unique_errors[:3]:  # Show first 3 unique errors
                    print(f"     - {error}")
        
        # Sample values for key fields
        print(f"\n📝 Sample Values for Key Fields:")
        key_fields = ['FullName', 'Email1Address', 'Email2Address', 'Email3Address', 
                     'CompanyName', 'JobTitle', 'BusinessTelephoneNumber']
        for field in key_fields:
            if field in self.property_values and self.property_values[field]:
                samples = list(set(self.property_values[field]))[:5]  # 5 unique samples
                print(f"   • {field}: {samples}")
    
    def save_detailed_report(self, contact_analyses, filename=None):
        """Save detailed analysis to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"contact_field_analysis_{timestamp}.json"
        
        report_data = {
            'analysis_info': {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_contacts_analyzed': len(contact_analyses),
                'total_properties_discovered': len(self.all_properties)
            },
            'property_summary': {
                'all_properties': sorted(list(self.all_properties)),
                'property_types': {prop: list(types) for prop, types in self.property_types.items()},
                'property_errors': dict(self.property_errors)
            },
            'contact_details': contact_analyses
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n💾 Detailed report saved to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return None


def main():
    """Main function to run the contact field debugger."""
    print("🔍 Outlook Contact Field Debugger")
    print("=" * 50)
    print("This tool will analyze all available properties on your Outlook contacts")
    print("to help identify the correct field names for extraction.\n")
    
    # Get number of contacts to analyze
    import sys
    max_contacts = 100
    if len(sys.argv) > 1:
        try:
            max_contacts = int(sys.argv[1])
            max_contacts = min(max_contacts, 500)  # Cap at 500 for safety
        except ValueError:
            print("⚠️ Invalid number provided, using default of 100")
    
    debugger = ContactFieldDebugger()
    
    # Run analysis
    contact_analyses = debugger.analyze_contacts(max_contacts)
    
    if contact_analyses:
        # Generate and display summary
        debugger.generate_summary_report(contact_analyses)
        
        # Save detailed report
        saved_file = debugger.save_detailed_report(contact_analyses)
        
        print(f"\n🎯 Key Findings for Email Fields:")
        print("Based on this analysis, you should update your extraction script to use:")
        
        # Analyze email field success
        email_success = {}
        for analysis in contact_analyses:
            for prop_name, prop_data in analysis['properties'].items():
                if 'email' in prop_name.lower() and prop_data.get('has_value', False):
                    email_success[prop_name] = email_success.get(prop_name, 0) + 1
        
        if email_success:
            print("\n📧 Recommended email field priorities:")
            for field, count in sorted(email_success.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {field}: Found values in {count} contacts")
        else:
            print("   ⚠️ No email fields found with values - this may indicate access issues")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Review the detailed report: {saved_file}")
        print(f"   2. Update your extraction script with working field names")
        print(f"   3. Focus on fields that have high availability and value counts")
        
    else:
        print("❌ Analysis failed - check Outlook connection and permissions")


if __name__ == "__main__":
    main() 