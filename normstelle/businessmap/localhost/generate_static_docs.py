#!/usr/bin/env python3
"""
Generate simple, static HTML documentation from OpenAPI JSON
This creates a fully functional offline API documentation viewer
"""

import json
import os
from pathlib import Path
import html

def load_openapi_spec():
    """Load the OpenAPI specification from JSON file"""
    json_path = Path("openapi_rendered/openapi.json")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading OpenAPI spec: {e}")
        return None

def generate_method_color(method):
    """Return CSS class for HTTP method colors"""
    colors = {
        'GET': 'method-get',
        'POST': 'method-post', 
        'PUT': 'method-put',
        'DELETE': 'method-delete',
        'PATCH': 'method-patch'
    }
    return colors.get(method.upper(), 'method-default')

def format_path_parameters(path, parameters):
    """Format path with parameter descriptions"""
    formatted = path
    param_info = []
    
    if parameters:
        for param in parameters:
            if param.get('in') == 'path':
                name = param.get('name', '')
                description = param.get('description', 'No description')
                param_info.append(f"<strong>{name}</strong>: {html.escape(description)}")
    
    return formatted, param_info

def generate_endpoint_html(path, method, operation, spec):
    """Generate HTML for a single endpoint"""
    summary = operation.get('summary', 'No summary')
    description = operation.get('description', '')
    parameters = operation.get('parameters', [])
    
    # Format the path and get parameter info
    formatted_path, path_params = format_path_parameters(path, parameters)
    
    html_content = f"""
    <div class="endpoint" id="{method.lower()}-{path.replace('/', '-').replace('{', '').replace('}', '')}">
        <div class="endpoint-header">
            <span class="method {generate_method_color(method)}">{method.upper()}</span>
            <span class="path">{html.escape(formatted_path)}</span>
        </div>
        
        <div class="endpoint-content">
            <h3>{html.escape(summary)}</h3>
            {f'<p class="description">{html.escape(description)}</p>' if description else ''}
            
            {f'''
            <div class="parameters">
                <h4>Path Parameters:</h4>
                <ul>
                    {"".join(f"<li>{param}</li>" for param in path_params)}
                </ul>
            </div>
            ''' if path_params else ''}
            
            {generate_parameters_section(parameters)}
            {generate_responses_section(operation.get('responses', {}))}
        </div>
    </div>
    """
    return html_content

def generate_parameters_section(parameters):
    """Generate HTML for parameters section"""
    if not parameters:
        return ""
    
    query_params = [p for p in parameters if p.get('in') == 'query']
    header_params = [p for p in parameters if p.get('in') == 'header']
    
    html_content = ""
    
    if query_params:
        html_content += """
        <div class="parameters">
            <h4>Query Parameters:</h4>
            <table class="params-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Required</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
        """
        for param in query_params:
            name = param.get('name', '')
            param_type = param.get('schema', {}).get('type', 'string')
            required = 'Yes' if param.get('required', False) else 'No'
            description = param.get('description', 'No description')
            
            html_content += f"""
                    <tr>
                        <td><code>{html.escape(name)}</code></td>
                        <td>{html.escape(param_type)}</td>
                        <td>{required}</td>
                        <td>{html.escape(description)}</td>
                    </tr>
            """
        html_content += """
                </tbody>
            </table>
        </div>
        """
    
    return html_content

def generate_responses_section(responses):
    """Generate HTML for responses section"""
    if not responses:
        return ""
    
    html_content = """
    <div class="responses">
        <h4>Responses:</h4>
        <div class="response-list">
    """
    
    for status_code, response in responses.items():
        description = response.get('description', 'No description')
        html_content += f"""
        <div class="response-item">
            <span class="status-code status-{status_code[0]}xx">{status_code}</span>
            <span class="response-description">{html.escape(description)}</span>
        </div>
        """
    
    html_content += """
        </div>
    </div>
    """
    return html_content

def generate_navigation(spec):
    """Generate navigation menu from API paths"""
    paths = spec.get('paths', {})
    nav_items = []
    
    # Group by tags if available
    tag_groups = {}
    
    for path, methods in paths.items():
        for method, operation in methods.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                tags = operation.get('tags', ['Other'])
                summary = operation.get('summary', f"{method.upper()} {path}")
                
                for tag in tags:
                    if tag not in tag_groups:
                        tag_groups[tag] = []
                    
                    endpoint_id = f"{method.lower()}-{path.replace('/', '-').replace('{', '').replace('}', '')}"
                    tag_groups[tag].append({
                        'id': endpoint_id,
                        'title': summary,
                        'method': method.upper(),
                        'path': path
                    })
    
    nav_html = '<div class="navigation">\n'
    
    for tag, endpoints in tag_groups.items():
        nav_html += f'<div class="nav-group">\n'
        nav_html += f'<h3 class="nav-group-title">{html.escape(tag)}</h3>\n'
        nav_html += f'<ul class="nav-list">\n'
        
        for endpoint in endpoints:
            nav_html += f'''
            <li class="nav-item">
                <a href="#{endpoint['id']}" class="nav-link">
                    <span class="method {generate_method_color(endpoint['method'])}">{endpoint['method']}</span>
                    <span class="nav-title">{html.escape(endpoint['title'])}</span>
                </a>
            </li>
            '''
        
        nav_html += '</ul>\n</div>\n'
    
    nav_html += '</div>\n'
    return nav_html

def generate_css():
    """Generate CSS styles for the documentation"""
    return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            display: flex;
            min-height: 100vh;
        }
        
        .sidebar {
            width: 300px;
            background: white;
            border-right: 1px solid #e1e5e9;
            padding: 20px;
            overflow-y: auto;
            position: fixed;
            height: 100vh;
        }
        
        .main-content {
            flex: 1;
            margin-left: 300px;
            padding: 20px;
            max-width: 1200px;
        }
        
        .header {
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #2d3748;
            margin-bottom: 10px;
        }
        
        .navigation {
            margin-top: 20px;
        }
        
        .nav-group {
            margin-bottom: 25px;
        }
        
        .nav-group-title {
            font-size: 14px;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .nav-list {
            list-style: none;
        }
        
        .nav-item {
            margin-bottom: 2px;
        }
        
        .nav-link {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            text-decoration: none;
            color: #4a5568;
            border-radius: 6px;
            transition: all 0.2s;
        }
        
        .nav-link:hover {
            background: #edf2f7;
        }
        
        .nav-title {
            margin-left: 10px;
            font-size: 13px;
        }
        
        .endpoint {
            background: white;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .endpoint-header {
            display: flex;
            align-items: center;
            padding: 20px;
            background: #f7fafc;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .method {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 60px;
            height: 24px;
            font-size: 11px;
            font-weight: 600;
            text-align: center;
            border-radius: 4px;
            margin-right: 15px;
        }
        
        .method-get { background: #48bb78; color: white; }
        .method-post { background: #4299e1; color: white; }
        .method-put { background: #ed8936; color: white; }
        .method-delete { background: #f56565; color: white; }
        .method-patch { background: #9f7aea; color: white; }
        .method-default { background: #718096; color: white; }
        
        .path {
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 16px;
            font-weight: 500;
            color: #2d3748;
        }
        
        .endpoint-content {
            padding: 20px;
        }
        
        .endpoint-content h3 {
            color: #2d3748;
            margin-bottom: 10px;
        }
        
        .description {
            color: #4a5568;
            margin-bottom: 20px;
        }
        
        .parameters {
            margin-bottom: 20px;
        }
        
        .parameters h4 {
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        .params-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        
        .params-table th,
        .params-table td {
            padding: 10px;
            border: 1px solid #e2e8f0;
            text-align: left;
        }
        
        .params-table th {
            background: #f7fafc;
            font-weight: 600;
            color: #2d3748;
        }
        
        .params-table code {
            background: #edf2f7;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 12px;
        }
        
        .responses {
            margin-top: 20px;
        }
        
        .responses h4 {
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        .response-item {
            display: flex;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .response-item:last-child {
            border-bottom: none;
        }
        
        .status-code {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 60px;
            height: 24px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 4px;
            margin-right: 15px;
        }
        
        .status-2xx { background: #48bb78; color: white; }
        .status-3xx { background: #4299e1; color: white; }
        .status-4xx { background: #ed8936; color: white; }
        .status-5xx { background: #f56565; color: white; }
        
        .response-description {
            color: #4a5568;
        }
        
        @media (max-width: 768px) {
            .sidebar {
                display: none;
            }
            
            .main-content {
                margin-left: 0;
            }
        }
    </style>
    """

def generate_static_docs():
    """Generate the complete static HTML documentation"""
    spec = load_openapi_spec()
    if not spec:
        return
    
    info = spec.get('info', {})
    title = info.get('title', 'API Documentation')
    description = info.get('description', '')
    version = info.get('version', '')
    
    # Generate navigation
    navigation = generate_navigation(spec)
    
    # Generate endpoint documentation
    endpoints_html = ""
    paths = spec.get('paths', {})
    
    for path, methods in paths.items():
        for method, operation in methods.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                endpoints_html += generate_endpoint_html(path, method, operation, spec)
    
    # Complete HTML document
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    {generate_css()}
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>API Documentation</h2>
            {navigation}
        </div>
        
        <div class="main-content">
            <div class="header">
                <h1>{html.escape(title)}</h1>
                {f'<p class="version">Version: {html.escape(version)}</p>' if version else ''}
                {f'<div class="description">{html.escape(description[:500])}...</div>' if description else ''}
            </div>
            
            <div class="endpoints">
                {endpoints_html}
            </div>
        </div>
    </div>
    
    <script>
        // Simple smooth scrolling for navigation links
        document.querySelectorAll('.nav-link').forEach(link => {{
            link.addEventListener('click', function(e) {{
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                if (targetElement) {{
                    targetElement.scrollIntoView({{ behavior: 'smooth' }});
                }}
            }});
        }});
    </script>
</body>
</html>"""
    
    # Write the static documentation
    output_dir = Path("static_docs")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "index.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_doc)
    
    print(f"✅ Static API documentation generated!")
    print(f"📁 Output: {output_file.absolute()}")
    print(f"🌐 Open {output_file.absolute()} in your browser to view")
    print(f"💡 This documentation works completely offline - no server needed!")

if __name__ == '__main__':
    generate_static_docs()










