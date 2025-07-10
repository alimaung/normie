#!/usr/bin/env python3
"""
Email Monitor - VBA JSON File Processor

This script monitors the folder where VBA exports JSON files and processes
new email data for analysis and debugging.
"""

import os
import json
import time
import datetime
from pathlib import Path
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

class EmailFileHandler(FileSystemEventHandler):
    """Handle file system events for new email JSON files."""
    
    def __init__(self, processor):
        self.processor = processor
        
    def on_created(self, event):
        """Handle new file creation."""
        if not event.is_directory and event.src_path.endswith('.json'):
            # Wait a bit for file to be fully written
            time.sleep(1)
            self.processor.process_new_file(event.src_path)
    
    def on_modified(self, event):
        """Handle file modification."""
        if not event.is_directory and event.src_path.endswith('.json'):
            # Wait a bit for file to be fully written
            time.sleep(1)
            self.processor.process_new_file(event.src_path)

class EmailMonitor:
    """Monitor and process VBA-generated email JSON files."""
    
    def __init__(self, watch_folder="C:\\temp\\outlook_extract"):
        self.watch_folder = Path(watch_folder)
        self.processed_files = set()
        self.email_database = {}
        self.statistics = {
            'total_files_processed': 0,
            'total_emails_found': 0,
            'accounts_discovered': set(),
            'latest_email_time': None,
            'processing_errors': []
        }
        
        # Create watch folder if it doesn't exist
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"Email Monitor initialized")
        print(f"Watching folder: {self.watch_folder}")
        
    def start_monitoring(self):
        """Start file system monitoring."""
        print("Starting real-time file monitoring...")
        
        # First, process any existing files
        self.process_existing_files()
        
        # Set up file watcher
        event_handler = EmailFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, str(self.watch_folder), recursive=False)
        observer.start()
        
        try:
            print("Monitor is running. Press Ctrl+C to stop.")
            while True:
                self.print_status()
                time.sleep(30)  # Print status every 30 seconds
        except KeyboardInterrupt:
            print("\nStopping monitor...")
            observer.stop()
        
        observer.join()
        print("Monitor stopped.")
    
    def process_existing_files(self):
        """Process any existing JSON files in the watch folder."""
        print("Processing existing files...")
        
        json_files = list(self.watch_folder.glob("*.json"))
        
        if not json_files:
            print("No existing files found.")
            return
        
        for file_path in sorted(json_files):
            self.process_new_file(str(file_path))
    
    def process_new_file(self, file_path):
        """Process a new or updated JSON file."""
        file_path = Path(file_path)
        
        # Skip if already processed this exact file
        file_key = f"{file_path.name}_{file_path.stat().st_mtime}"
        if file_key in self.processed_files:
            return
        
        print(f"\n📧 Processing file: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.process_email_data(data, file_path)
            self.processed_files.add(file_key)
            self.statistics['total_files_processed'] += 1
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error in {file_path.name}: {str(e)}"
            print(f"❌ {error_msg}")
            self.statistics['processing_errors'].append(error_msg)
            
        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {str(e)}"
            print(f"❌ {error_msg}")
            self.statistics['processing_errors'].append(error_msg)
    
    def process_email_data(self, data, file_path):
        """Process email data from JSON."""
        folder_name = data.get('folder_name', 'Unknown')
        folder_path = data.get('folder_path', 'Unknown')
        total_items = data.get('total_items', 0)
        emails = data.get('emails', [])
        extracted_count = data.get('extracted_count', 0)
        
        print(f"  📁 Folder: {folder_name}")
        print(f"  📊 Total items: {total_items}, Extracted: {extracted_count}")
        
        # Determine account name from file path
        account_name = self.extract_account_name(file_path.name)
        self.statistics['accounts_discovered'].add(account_name)
        
        # Store emails in database
        if account_name not in self.email_database:
            self.email_database[account_name] = {}
        
        if folder_name not in self.email_database[account_name]:
            self.email_database[account_name][folder_name] = []
        
        # Process individual emails
        new_emails = 0
        for email in emails:
            if self.is_new_email(email, account_name, folder_name):
                self.email_database[account_name][folder_name].append(email)
                self.print_email_summary(email, account_name, folder_name)
                new_emails += 1
                self.statistics['total_emails_found'] += 1
                
                # Update latest email time
                received_time = email.get('received_time')
                if received_time and (not self.statistics['latest_email_time'] or 
                                    received_time > self.statistics['latest_email_time']):
                    self.statistics['latest_email_time'] = received_time
        
        if new_emails > 0:
            print(f"  ✅ Added {new_emails} new emails to database")
        else:
            print(f"  ℹ️  No new emails (may be duplicates)")
    
    def extract_account_name(self, filename):
        """Extract account name from filename."""
        # Filename format: accountname_inbox_timestamp.json
        parts = filename.split('_')
        if len(parts) >= 2:
            return parts[0]
        return "Unknown"
    
    def is_new_email(self, email, account_name, folder_name):
        """Check if this email is new (not already in database)."""
        if account_name not in self.email_database:
            return True
        
        if folder_name not in self.email_database[account_name]:
            return True
        
        # Check for duplicate based on subject + received_time + sender
        email_signature = (
            email.get('subject', ''),
            email.get('received_time', ''),
            email.get('sender_email', '')
        )
        
        for existing_email in self.email_database[account_name][folder_name]:
            existing_signature = (
                existing_email.get('subject', ''),
                existing_email.get('received_time', ''),
                existing_email.get('sender_email', '')
            )
            
            if email_signature == existing_signature:
                return False
        
        return True
    
    def print_email_summary(self, email, account_name, folder_name):
        """Print a summary of an email for debugging."""
        subject = email.get('subject', 'No Subject')[:60]
        sender_name = email.get('sender_name', 'Unknown')
        sender_email = email.get('sender_email', 'Unknown')
        received_time = email.get('received_time', 'Unknown')
        size = email.get('size', 0)
        unread = email.get('unread', False)
        body_preview = email.get('body', '')[:100]
        
        print(f"    📨 {subject}")
        print(f"      👤 From: {sender_name} ({sender_email})")
        print(f"      🕒 Time: {received_time}")
        print(f"      📏 Size: {size} bytes {'[UNREAD]' if unread else ''}")
        
        # Show recipients if available
        recipients = email.get('recipients', [])
        if recipients:
            recipient_names = [r.get('name', 'Unknown') for r in recipients[:3]]
            print(f"      👥 To: {', '.join(recipient_names)}")
            if len(recipients) > 3:
                print(f"           (+{len(recipients) - 3} more)")
        
        # Show attachments if available
        attachments = email.get('attachments', [])
        if attachments:
            attachment_names = [a.get('filename', 'Unknown') for a in attachments[:3]]
            print(f"      📎 Attachments: {', '.join(attachment_names)}")
            if len(attachments) > 3:
                print(f"                     (+{len(attachments) - 3} more)")
        
        # Show body preview if available
        if body_preview.strip():
            print(f"      💬 Preview: {body_preview.strip()}...")
        
        print()
    
    def print_status(self):
        """Print current status."""
        print(f"\n🔍 Monitor Status - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Files processed: {self.statistics['total_files_processed']}")
        print(f"📧 Total emails: {self.statistics['total_emails_found']}")
        print(f"👤 Accounts: {len(self.statistics['accounts_discovered'])}")
        
        if self.statistics['accounts_discovered']:
            print(f"   {', '.join(sorted(self.statistics['accounts_discovered']))}")
        
        if self.statistics['latest_email_time']:
            print(f"🕒 Latest email: {self.statistics['latest_email_time']}")
        
        if self.statistics['processing_errors']:
            print(f"❌ Errors: {len(self.statistics['processing_errors'])}")
        
        # Show recent emails from each account
        for account_name, folders in self.email_database.items():
            total_emails = sum(len(emails) for emails in folders.values())
            print(f"   📊 {account_name}: {total_emails} emails")
            
            for folder_name, emails in folders.items():
                if emails:
                    latest_email = max(emails, key=lambda x: x.get('received_time', ''))
                    subject = latest_email.get('subject', 'No Subject')[:40]
                    print(f"      📁 {folder_name}: {len(emails)} emails, latest: '{subject}...'")
    
    def save_database(self, output_file="email_database.json"):
        """Save the email database to a file."""
        try:
            output_path = self.watch_folder / output_file
            
            # Convert sets to lists for JSON serialization
            stats_copy = self.statistics.copy()
            stats_copy['accounts_discovered'] = list(stats_copy['accounts_discovered'])
            
            database_export = {
                'timestamp': datetime.datetime.now().isoformat(),
                'statistics': stats_copy,
                'emails': self.email_database
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(database_export, f, indent=2, default=str)
            
            print(f"💾 Database saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error saving database: {str(e)}")
            return None
    
    def run_once(self):
        """Process files once and exit (for testing)."""
        print("Running one-time processing...")
        self.process_existing_files()
        self.print_status()
        self.save_database()

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor VBA-generated email JSON files')
    parser.add_argument('--folder', default='C:\\temp\\outlook_extract', 
                      help='Folder to monitor (default: C:\\temp\\outlook_extract)')
    parser.add_argument('--once', action='store_true', 
                      help='Process once and exit (no monitoring)')
    
    args = parser.parse_args()
    
    print("Outlook Email Monitor")
    print("=" * 40)
    
    monitor = EmailMonitor(args.folder)
    
    try:
        if args.once:
            monitor.run_once()
        else:
            monitor.start_monitoring()
    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        monitor.save_database()

if __name__ == "__main__":
    main() 