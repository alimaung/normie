#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler,HTTPServer
import argparse, os, random, sys, requests

from socketserver import ThreadingMixIn
import threading


# Changed to proxy to localhost:1918 instead of Wikipedia
target_host = 'localhost'
target_port = 1918
# Add the expected hostname
expected_hostname = 'rolls-royce.norm'

def merge_two_dicts(x, y):
    return x | y

def set_header():
    headers = {
        'Host': f'{target_host}:{target_port}'
    }

    return headers

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
    
    def check_hostname(self):
        """Check if the request is for the expected hostname"""
        host_header = self.headers.get('Host', '').split(':')[0]  # Remove port if present
        if expected_hostname and host_header != expected_hostname:
            return False
        return True
    
    def do_HEAD(self):
        self.do_GET(body=False)
        return
        
    def do_GET(self, body=True):
        sent = False
        try:
            # Check hostname if specified
            if not self.check_hostname():
                self.send_error(404, f'Host not found. Expected: {expected_hostname}')
                return
                
            # Changed to proxy to localhost:1918 instead of Wikipedia
            url = f'http://{target_host}:{target_port}{self.path}'
            req_header = self.parse_headers()

            print(req_header)
            print(url)
            resp = requests.get(url, headers=merge_two_dicts(req_header, set_header()), verify=False)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            msg = resp.text
            if body:
                self.wfile.write(msg.encode(encoding='UTF-8',errors='strict'))
            return
        finally:
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def do_POST(self, body=True):
        sent = False
        try:
            # Check hostname if specified
            if not self.check_hostname():
                self.send_error(404, f'Host not found. Expected: {expected_hostname}')
                return
                
            # Changed to proxy to localhost:1918 instead of Wikipedia
            url = f'http://{target_host}:{target_port}{self.path}'
            content_len = int(self.headers.getheader('content-length', 0))
            post_body = self.rfile.read(content_len)
            req_header = self.parse_headers()

            resp = requests.post(url, data=post_body, headers=merge_two_dicts(req_header, set_header()), verify=False)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            if body:
                self.wfile.write(resp.content)
            return
        finally:
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def parse_headers(self):
        req_header = {}
        for line in self.headers:
            line_parts = [o.strip() for o in line.split(':', 1)]
            if len(line_parts) == 2:
                req_header[line_parts[0]] = line_parts[1]
        return req_header

    def send_resp_headers(self, resp):
        respheaders = resp.headers
        print ('Response Header')
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length', 'Content-Length']:
                print (key, respheaders[key])
                self.send_header(key, respheaders[key])
        self.send_header('Content-Length', len(resp.content))
        self.end_headers()

def parse_args(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Proxy HTTP requests')
    # Changed default port to 80 to match typical reverse proxy setup
    parser.add_argument('--port', dest='port', type=int, default=80,
                        help='serve HTTP requests on specified port (default: 80)')
    # Updated help text and default
    parser.add_argument('--target-host', dest='target_host', type=str, default='localhost',
                        help='target hostname to proxy to (default: localhost)')
    parser.add_argument('--target-port', dest='target_port', type=int, default=1918,
                        help='target port to proxy to (default: 1918)')
    parser.add_argument('--hostname', dest='hostname', type=str, default='rolls-royce.norm',
                        help='expected hostname for incoming requests (default: rolls-royce.norm)')
    args = parser.parse_args(argv)
    return args

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def main(argv=sys.argv[1:]):
    global target_host, target_port, expected_hostname
    args = parse_args(argv)
    target_host = args.target_host
    target_port = args.target_port
    expected_hostname = args.hostname
    print(f'http server is starting on port {args.port}...')
    print(f'expected hostname: {expected_hostname}')
    print(f'reverse proxying to {target_host}:{target_port}')
    server_address = ('0.0.0.0', args.port)  # Changed to bind to all interfaces
    httpd = ThreadedHTTPServer(server_address, ProxyHTTPRequestHandler)
    print('http server is running as reverse proxy')
    httpd.serve_forever()

if __name__ == '__main__':
    main()