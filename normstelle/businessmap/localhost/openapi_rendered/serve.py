#!/usr/bin/env python3
"""
Simple HTTP server to serve the OpenAPI documentation locally
Run this script and navigate to http://localhost:8000
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_openapi_docs():
    """Start a local HTTP server for the OpenAPI documentation"""
    
    # Change to the directory containing the HTML files
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Add CORS headers to handle any cross-origin issues
    class CORSRequestHandler(Handler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            super().end_headers()
    
    try:
        with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
            print(f"🚀 OpenAPI Documentation Server Started!")
            print(f"📡 Serving at: http://localhost:{PORT}")
            print(f"📁 Directory: {script_dir}")
            print(f"🌐 Opening browser...")
            print(f"💡 Press Ctrl+C to stop the server")
            
            # Automatically open the browser
            webbrowser.open(f'http://localhost:{PORT}')
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use. Please close other applications using this port or change the PORT variable.")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    serve_openapi_docs()
