#!/usr/bin/env python3
"""
ChemScan PDF Upload Script
Configurable script to base64 encode PDFs and upload them to ChemScan
"""

import os
import uuid
import base64
import requests
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class UploadConfig:
    """Configuration for ChemScan upload"""
    # File Configuration
    pdf_path: str = "001-2024_01040645_Freigabe.pdf"  # Default PDF file path
    
    # URL Configuration
    base_url: str = "https://app.chemscan.de"
    entity_id: str = "2177"  # The ID in the URL path
    
    # Authentication & Security
    csrf_token: str = "R8ZUfQSDav-G52HCcPjAGTVoV7TXPJfAnnxf5axhZNg"
    cookies: Dict[str, str] = None
    
    # Widget Configuration
    widget_id: str = None  # Will be auto-generated if None
    widget_container: str = "dialog"
    widget_init: str = "1"
    
    # Upload Parameters
    comment: str = "TEST"
    owner_id: str = "303"
    form_token: str = "e3c0ece.BjvK3egWitenmERfr5-5vIRVRFyz3MnSLSLyuyOhFWA.R2yb5Nov_OWS33UH_abA69cvDw2Aha-0fA-e6FuTcVlFeJqIh0O-5p_oEQ"
    
    def __post_init__(self):
        """Initialize default values after creation"""
        if self.cookies is None:
            # Default cookies from the PowerShell script
            self.cookies = {
                'BAPRM': 'YUtHOFUwTWcxTjduemd1UnA4VHdMTEpMTktXSkdrdjFOUzVWbjc1aVUzOGR3dUlZa1NLa1cxOUNSdmk2aUhSQWtIZDh1T3lremYyTEY3dndsZ2xDcUE9PTptQjFWR3pGbU9HWUtXZHpwKzhVSjZpcXIxYXdmOW1ON0FUdkVrWWt5V2l1TC9BZUljVzNuazJwUkx3RmpBLzErbW9IZHFmTFVYQ2ZkOHYvMTNQQzVGdz09',
                'BAPID': 'e201cf681d7e8ebbba545d5ae6b74b64',
                'https-_csrf': 'R8ZUfQSDav-G52HCcPjAGTVoV7TXPJfAnnxf5axhZNg'
            }
        
        if self.widget_id is None:
            self.widget_id = str(uuid.uuid4())


class ChemScanUploader:
    """
    ChemScan PDF Uploader with configurable parameters
    """
    
    def __init__(self, config: UploadConfig = None):
        self.config = config or UploadConfig()
        self.session = requests.Session()
        
        # Set up session with cookies
        for name, value in self.config.cookies.items():
            self.session.cookies.set(name, value, domain='app.chemscan.de')
    
    def generate_boundary(self) -> str:
        """Generate a WebKit-style boundary"""
        random_chars = str(uuid.uuid4()).replace('-', '')[:16]
        return f"----WebKitFormBoundary{random_chars}"
    
    def encode_pdf_base64(self, pdf_path: str) -> tuple[str, str]:
        """
        Read PDF file and encode as base64
        
        Returns:
            tuple: (base64_content, filename)
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        filename = os.path.basename(pdf_path)
        
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            base64_content = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return base64_content, filename
    
    def build_multipart_data(self, pdf_path: str) -> tuple[bytes, str]:
        """
        Build multipart/form-data payload exactly like the PowerShell script
        
        Returns:
            tuple: (binary_data, boundary)
        """
        boundary = self.generate_boundary()
        base64_content, filename = self.encode_pdf_base64(pdf_path)
        
        parts = []
        
        # File upload part (with base64 encoded content)
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="oro_attachment[file][file]"; filename="{filename}"\r\n'.encode())
        parts.append(b'Content-Type: application/pdf\r\n\r\n')
        parts.append(base64_content.encode('utf-8'))
        parts.append(b'\r\n')
        
        # Empty file part
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(b'Content-Disposition: form-data; name="oro_attachment[file][emptyFile]"\r\n\r\n')
        parts.append(b'\r\n')
        
        # Comment part
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(b'Content-Disposition: form-data; name="oro_attachment[comment]"\r\n\r\n')
        parts.append(self.config.comment.encode('utf-8'))
        parts.append(b'\r\n')
        
        # Owner part
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(b'Content-Disposition: form-data; name="oro_attachment[owner]"\r\n\r\n')
        parts.append(self.config.owner_id.encode())
        parts.append(b'\r\n')
        
        # Token part
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(b'Content-Disposition: form-data; name="oro_attachment[_token]"\r\n\r\n')
        parts.append(self.config.form_token.encode())
        parts.append(b'\r\n')
        
        # Widget container part
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(b'Content-Disposition: form-data; name="_widgetContainer"\r\n\r\n')
        parts.append(self.config.widget_container.encode())
        parts.append(b'\r\n')
        
        # Widget ID part
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(b'Content-Disposition: form-data; name="_wid"\r\n\r\n')
        parts.append(self.config.widget_id.encode())
        parts.append(b'\r\n')
        
        # Widget init part
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(b'Content-Disposition: form-data; name="_widgetInit"\r\n\r\n')
        parts.append(b'0\r\n')
        
        # Final boundary
        parts.append(f"--{boundary}--\r\n".encode())
        
        return b''.join(parts), boundary
    
    def build_headers(self, boundary: str) -> Dict[str, str]:
        """Build HTTP headers for the request"""
        return {
            'authority': 'app.chemscan.de',
            'method': 'POST',
            'path': f'/attachment/create/UUB_Bundle_CadasterBundle_Entity_HazardSubstanceOrganization/{self.config.entity_id}',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache, no-store',
            'content-type': f'multipart/form-data; boundary={boundary}',
            'origin': 'https://app.chemscan.de',
            'priority': 'u=1, i',
            'referer': f'https://app.chemscan.de/cadaster/organization/view/{self.config.entity_id}',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'x-csrf-header': self.config.csrf_token,
            'x-requested-with': 'XMLHttpRequest'
        }
    
    def build_url(self) -> str:
        """Build the upload URL with query parameters"""
        base_url = f"{self.config.base_url}/attachment/create/UUB_Bundle_CadasterBundle_Entity_HazardSubstanceOrganization/{self.config.entity_id}"
        params = {
            '_widgetContainer': self.config.widget_container,
            '_wid': self.config.widget_id,
            '_widgetInit': self.config.widget_init
        }
        
        # Build query string manually to match the original format
        query_parts = [f"{k}={v}" for k, v in params.items()]
        return f"{base_url}?{'&'.join(query_parts)}"
    
    def upload_pdf(self, pdf_path: str = None, comment: str = None, dry_run: bool = False) -> requests.Response:
        """
        Upload PDF file to ChemScan
        
        Args:
            pdf_path: Path to the PDF file (uses config default if None)
            comment: Upload comment (uses config default if None)
            dry_run: If True, only prepare the request but don't send it
            
        Returns:
            requests.Response object
        """
        # Use provided parameters or fall back to config defaults
        pdf_path = pdf_path or self.config.pdf_path
        if comment is not None:
            original_comment = self.config.comment
            self.config.comment = comment
        
        print(f"Preparing upload for: {pdf_path}")
        print(f"Entity ID: {self.config.entity_id}")
        print(f"Widget ID: {self.config.widget_id}")
        print(f"Comment: {self.config.comment}")
        
        # Build multipart data
        binary_data, boundary = self.build_multipart_data(pdf_path)
        print(f"Multipart data size: {len(binary_data):,} bytes")
        
        # Build request components
        url = self.build_url()
        headers = self.build_headers(boundary)
        
        print(f"Upload URL: {url}")
        
        if dry_run:
            print("DRY RUN - Request prepared but not sent")
            print(f"Headers: {json.dumps(headers, indent=2)}")
            print(f"Cookies: {dict(self.session.cookies)}")
            return None
        
        # Make the request
        print("Sending request...")
        response = self.session.post(
            url,
            data=binary_data,
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Restore original comment if it was temporarily changed
        if comment is not None:
            self.config.comment = original_comment
        
        return response
    
    def update_config(self, **kwargs):
        """Update configuration parameters"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                print(f"Updated {key}: {value}")
            else:
                print(f"Warning: Unknown config parameter '{key}'")
    
    def save_config(self, config_path: str = "upload_config.json"):
        """Save current configuration to JSON file"""
        config_dict = asdict(self.config)
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        print(f"Configuration saved to: {config_path}")
    
    @classmethod
    def load_config(cls, config_path: str = "upload_config.json") -> 'ChemScanUploader':
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        
        config = UploadConfig(**config_dict)
        return cls(config)


def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload PDF to ChemScan')
    parser.add_argument('pdf_path', nargs='?', help='Path to PDF file (optional if set in config)')
    parser.add_argument('--entity-id', help='Entity ID (e.g., 2177)')
    parser.add_argument('--comment', help='Upload comment')
    parser.add_argument('--csrf-token', help='CSRF token for authentication')
    parser.add_argument('--widget-id', help='Widget ID (auto-generated if not provided)')
    parser.add_argument('--owner-id', help='Owner ID (default: 303)')
    parser.add_argument('--dry-run', action='store_true', help='Prepare request but don\'t send')
    parser.add_argument('--config', help='Load configuration from JSON file')
    parser.add_argument('--save-config', help='Save current configuration to JSON file')
    parser.add_argument('--randomize-widget', action='store_true', help='Generate new random widget ID')
    
    args = parser.parse_args()
    
    # Load or create configuration
    if args.config and os.path.exists(args.config):
        uploader = ChemScanUploader.load_config(args.config)
        print(f"Configuration loaded from: {args.config}")
    else:
        config = UploadConfig()
        uploader = ChemScanUploader(config)
    
    # Update configuration with command line arguments
    config_updates = {}
    if args.pdf_path:
        config_updates['pdf_path'] = args.pdf_path
    if args.entity_id:
        config_updates['entity_id'] = args.entity_id
    if args.comment:
        config_updates['comment'] = args.comment
    if args.csrf_token:
        config_updates['csrf_token'] = args.csrf_token
    if args.widget_id:
        config_updates['widget_id'] = args.widget_id
    if args.owner_id:
        config_updates['owner_id'] = args.owner_id
    if args.randomize_widget:
        config_updates['widget_id'] = str(uuid.uuid4())
    
    if config_updates:
        uploader.update_config(**config_updates)
    
    # Save configuration if requested
    if args.save_config:
        uploader.save_config(args.save_config)
    
    # Determine PDF path
    pdf_path = args.pdf_path or uploader.config.pdf_path
    if not pdf_path:
        print("❌ Error: No PDF path specified. Use command line argument or set in config.")
        return
    
    # Perform upload
    try:
        response = uploader.upload_pdf(pdf_path, dry_run=args.dry_run)
        
        if response and not args.dry_run:
            if response.status_code == 200:
                print("✅ Upload successful!")
            else:
                print(f"❌ Upload failed with status {response.status_code}")
                print(f"Response: {response.text[:500]}...")
                
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Example usage when run directly
    if len(os.sys.argv) == 1:
        # No command line args, run example
        print("ChemScan PDF Uploader")
        print("=" * 50)
        
        # Create example configuration
        config = UploadConfig(
            pdf_path="001-2024_01040645_Freigabe.pdf",
            entity_id="2177",
            comment="Automated upload test",
            # Cookies are populated with defaults from PowerShell script
        )
        
        uploader = ChemScanUploader(config)
        
        # Show configuration
        print("Current Configuration:")
        print(f"  PDF Path: {config.pdf_path}")
        print(f"  Entity ID: {config.entity_id}")
        print(f"  Widget ID: {config.widget_id}")
        print(f"  Comment: {config.comment}")
        print(f"  Base URL: {config.base_url}")
        print(f"  Owner ID: {config.owner_id}")
        print()
        
        # Example with the PDF file
        pdf_path = config.pdf_path
        
        if os.path.exists(pdf_path):
            print(f"Found PDF: {pdf_path}")
            
            # Dry run first
            print("\n--- DRY RUN ---")
            uploader.upload_pdf(pdf_path, dry_run=True)
            
            # Uncomment to actually upload:
            # print("\n--- ACTUAL UPLOAD ---")
            # response = uploader.upload_pdf(pdf_path)
            
        else:
            print(f"PDF file not found: {pdf_path}")
            print("Place your PDF file in the same directory or use command line arguments.")
        
        print("\nUsage examples:")
        print("  python chemscan_upload.py your_file.pdf")
        print("  python chemscan_upload.py your_file.pdf --entity-id 1234 --comment 'My upload'")
        print("  python chemscan_upload.py your_file.pdf --dry-run")
        print("  python chemscan_upload.py --config my_config.json")
        print("  python chemscan_upload.py your_file.pdf --randomize-widget --comment 'New test'")
        print("  python chemscan_upload.py --save-config my_config.json")
    else:
        main()
