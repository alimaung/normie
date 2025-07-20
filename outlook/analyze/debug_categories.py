#!/usr/bin/env python3
"""
Debug Categories Script

Tests various methods to access custom Outlook categories for the IRM account.
This will help determine if we can access the custom categories set up in Outlook.
"""

import win32com.client
import pythoncom
import traceback

def debug_categories():
    """Debug function to explore Outlook categories using different approaches."""
    
    print("Outlook Categories Debug")
    print("=" * 40)
    
    try:
        # Initialize COM
        pythoncom.CoInitialize()
        print("✓ COM initialized")
        
        # Get Outlook application and namespace
        app = win32com.client.Dispatch("Outlook.Application")
        namespace = app.GetNamespace("MAPI")
        print("✓ Connected to Outlook")
        
        # Method 1: Try namespace.Categories (Master Category List)
        print("\n" + "=" * 40)
        print("METHOD 1: Namespace Categories")
        print("=" * 40)
        
        try:
            categories = namespace.Categories
            print(f"✓ Categories object: {categories}")
            print(f"✓ Categories count: {categories.Count}")
            
            if categories.Count > 0:
                print("\nCustom Categories Found:")
                print("-" * 30)
                for i in range(1, min(categories.Count + 1, 20)):  # Limit to first 20
                    try:
                        cat = categories.Item(i)
                        color = getattr(cat, 'Color', 'Unknown')
                        shortcut_key = getattr(cat, 'ShortcutKey', 'None')
                        category_type = getattr(cat, 'CategoryType', 'Unknown')
                        
                        print(f"  {i:2d}. Name: '{cat.Name}'")
                        print(f"      Color: {color}")
                        print(f"      Shortcut: {shortcut_key}")
                        print(f"      Type: {category_type}")
                        print()
                        
                    except Exception as e:
                        print(f"  {i:2d}. Error accessing category: {str(e)}")
            else:
                print("No categories found in namespace.Categories")
                
        except Exception as e:
            print(f"✗ Error accessing namespace.Categories: {str(e)}")
            print(f"Stack trace: {traceback.format_exc()}")
        
        # Method 2: Try through Store Categories
        print("\n" + "=" * 40)
        print("METHOD 2: Store Categories")
        print("=" * 40)
        
        try:
            # Get all stores
            stores = namespace.Stores
            print(f"✓ Found {stores.Count} stores")
            
            for i in range(1, stores.Count + 1):
                try:
                    store = stores.Item(i)
                    print(f"\nStore {i}: {store.DisplayName}")
                    
                    # Check if this is the IRM store
                    if 'irm' in store.DisplayName.lower() or 'standardisation' in store.DisplayName.lower():
                        print(f"  ★ This looks like the IRM store!")
                        
                        # Try to access store categories
                        try:
                            store_categories = store.Categories
                            print(f"  ✓ Store categories count: {store_categories.Count}")
                            
                            for j in range(1, min(store_categories.Count + 1, 10)):
                                cat = store_categories.Item(j)
                                print(f"    {j}. {cat.Name} (Color: {getattr(cat, 'Color', 'Unknown')})")
                                
                        except Exception as e:
                            print(f"  ✗ Error accessing store categories: {str(e)}")
                    
                except Exception as e:
                    print(f"  ✗ Error accessing store {i}: {str(e)}")
                    
        except Exception as e:
            print(f"✗ Error accessing stores: {str(e)}")
        
        # Method 3: Try through a sample email's categories
        print("\n" + "=" * 40)
        print("METHOD 3: Sample Email Categories")
        print("=" * 40)
        
        try:
            # Get inbox
            inbox = namespace.GetDefaultFolder(6)  # olFolderInbox
            print(f"✓ Got inbox: {inbox.Name}")
            
            items = inbox.Items
            items.Sort("[ReceivedTime]", True)
            
            # Look at first few emails
            sample_categories = set()
            
            for i in range(1, min(items.Count + 1, 10)):
                try:
                    item = items.Item(i)
                    if hasattr(item, 'Categories') and item.Categories:
                        categories_str = item.Categories
                        print(f"  Email {i}: '{item.Subject[:50]}...'")
                        print(f"    Categories: '{categories_str}'")
                        
                        # Parse categories
                        if categories_str:
                            cats = [cat.strip() for cat in categories_str.split(',') if cat.strip()]
                            sample_categories.update(cats)
                            
                except Exception as e:
                    print(f"  Email {i}: Error - {str(e)}")
            
            if sample_categories:
                print(f"\nUnique categories found in emails:")
                for cat in sorted(sample_categories):
                    print(f"  - '{cat}'")
            else:
                print("No categories found in sample emails")
                
        except Exception as e:
            print(f"✗ Error checking sample emails: {str(e)}")
        
        # Method 4: Try Application.Categories
        print("\n" + "=" * 40)
        print("METHOD 4: Application Categories")
        print("=" * 40)
        
        try:
            app_categories = app.Categories
            print(f"✓ Application categories count: {app_categories.Count}")
            
            if app_categories.Count > 0:
                print("\nApplication Categories:")
                print("-" * 25)
                for i in range(1, min(app_categories.Count + 1, 15)):
                    try:
                        cat = app_categories.Item(i)
                        print(f"  {i:2d}. '{cat.Name}' (Color: {getattr(cat, 'Color', 'Unknown')})")
                    except Exception as e:
                        print(f"  {i:2d}. Error: {str(e)}")
            
        except Exception as e:
            print(f"✗ Error accessing app.Categories: {str(e)}")
        
        # Method 5: Check account-specific categories
        print("\n" + "=" * 40)
        print("METHOD 5: Account-Specific Categories")
        print("=" * 40)
        
        try:
            accounts = namespace.Accounts
            print(f"✓ Found {accounts.Count} accounts")
            
            for i in range(1, accounts.Count + 1):
                try:
                    account = accounts.Item(i)
                    print(f"\nAccount {i}: {account.DisplayName}")
                    print(f"  Email: {getattr(account, 'SmtpAddress', 'Unknown')}")
                    
                    # Check if this is the IRM account
                    smtp_address = getattr(account, 'SmtpAddress', '').lower()
                    if 'irm' in smtp_address or 'standardisation' in smtp_address:
                        print(f"  ★ This is the IRM account!")
                        
                        # Try to access account store
                        try:
                            delivery_store = account.DeliveryStore
                            print(f"  Store: {delivery_store.DisplayName}")
                            
                            # Try store categories
                            try:
                                store_cats = delivery_store.Categories
                                print(f"  Store categories: {store_cats.Count}")
                            except:
                                print(f"  Store categories: Not accessible")
                                
                        except Exception as e:
                            print(f"  ✗ Error accessing account store: {str(e)}")
                    
                except Exception as e:
                    print(f"  ✗ Error accessing account {i}: {str(e)}")
                    
        except Exception as e:
            print(f"✗ Error accessing accounts: {str(e)}")
        
        print("\n" + "=" * 40)
        print("SUMMARY")
        print("=" * 40)
        print("This debug script tested 5 different methods to access Outlook categories:")
        print("1. Namespace.Categories (Master Category List)")
        print("2. Store.Categories (Per-store categories)")
        print("3. Email.Categories (Categories from actual emails)")
        print("4. Application.Categories (Application-level categories)")
        print("5. Account.Store.Categories (Account-specific categories)")
        print("\nCheck the output above to see which methods worked and what categories were found.")
        
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")
    
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

if __name__ == "__main__":
    debug_categories() 