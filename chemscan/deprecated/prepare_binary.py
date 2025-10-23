import os
import uuid
import base64

def generate_multipart_binary(
    pdf_path: str,
    comment: str = "TEST",
    owner_id: str = "303",
    form_token: str = "e3c0ece.BjvK3egWitenmERfr5-5vIRVRFyz3MnSLSLyuyOhFWA.R2yb5Nov_OWS33UH_abA69cvDw2Aha-0fA-e6FuTcVlFeJqIh0O-5p_oEQ",
    widget_id: str = None
) -> tuple[bytes, str]:
    """
    Generate the exact binary multipart/form-data payload
    
    Returns:
        tuple: (binary_data, boundary)
    """
    
    if widget_id is None:
        widget_id = str(uuid.uuid4())
    
    # Generate boundary (similar to WebKit)
    boundary = f"----WebKitFormBoundary{''.join([chr(ord(c)) for c in str(uuid.uuid4()).replace('-', '')[:16]])}"
    
    # Read PDF file and encode as Base64
    filename = os.path.basename(pdf_path)
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()
        pdf_content = base64.b64encode(pdf_bytes).decode('utf-8')
    
    # Build multipart data
    parts = []
    
    # File upload part (with Base64 encoded content)
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(f'Content-Disposition: form-data; name="oro_attachment[file][file]"; filename="{filename}"\r\n'.encode())
    parts.append(b'Content-Type: application/pdf\r\n\r\n')
    parts.append(pdf_content.encode('utf-8'))  # Base64 string as UTF-8 bytes
    parts.append(b'\r\n')
    
    # Empty file part
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(b'Content-Disposition: form-data; name="oro_attachment[file][emptyFile]"\r\n\r\n')
    parts.append(b'\r\n')
    
    # Comment part
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(b'Content-Disposition: form-data; name="oro_attachment[comment]"\r\n\r\n')
    parts.append(comment.encode('utf-8'))
    parts.append(b'\r\n')
    
    # Owner part
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(b'Content-Disposition: form-data; name="oro_attachment[owner]"\r\n\r\n')
    parts.append(owner_id.encode())
    parts.append(b'\r\n')
    
    # Token part
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(b'Content-Disposition: form-data; name="oro_attachment[_token]"\r\n\r\n')
    parts.append(form_token.encode())
    parts.append(b'\r\n')
    
    # Widget container part
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(b'Content-Disposition: form-data; name="_widgetContainer"\r\n\r\n')
    parts.append(b'dialog\r\n')
    
    # Widget ID part
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(b'Content-Disposition: form-data; name="_wid"\r\n\r\n')
    parts.append(widget_id.encode())
    parts.append(b'\r\n')
    
    # Widget init part
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(b'Content-Disposition: form-data; name="_widgetInit"\r\n\r\n')
    parts.append(b'0\r\n')
    
    # Final boundary
    parts.append(f"--{boundary}--\r\n".encode())
    
    # Combine all parts
    binary_data = b''.join(parts)
    
    return binary_data, boundary


def save_binary_to_file(pdf_path: str, output_path: str = None):
    """
    Generate binary data and save to file for inspection
    """
    if output_path is None:
        output_path = "multipart_payload.bin"
    
    binary_data, boundary = generate_multipart_binary(pdf_path)
    
    with open(output_path, 'wb') as f:
        f.write(binary_data)
    
    print(f"Binary payload saved to: {output_path}")
    print(f"Boundary: {boundary}")
    print(f"Size: {len(binary_data):,} bytes")
    
    return binary_data, boundary


def upload_with_binary(
    pdf_path: str,
    entity_id: int = 2177,
    csrf_token: str = "R8ZUfQSDav-G52HCcPjAGTVoV7TXPJfAnnxf5axhZNg",
    cookies: dict = None
):
    """
    Upload using raw binary data (like PowerShell does)
    """
    import requests
    
    if cookies is None:
        cookies = {
            'BAPRM': 'YUtHOFUwTWcxTjduemd1UnA4VHdMTEpMTktXSkdrdjFOUzVWbjc1aVUzOGR3dUlZa1NLa1cxOUNSdmk2aUhSQWtIZDh1T3lremYyTEY3dndsZ2xDcUE9PTptQjFWR3pGbU9HWUtXZHpwKzhVSjZpcXIxYXdmOW1ON0FUdkVrWWt5V2l1TC9BZUljVzNuazJwUkx3RmpBLzErbW9IZHFmTFVYQ2ZkOHYvMTNQQzVGdz09',
            'BAPID': 'e201cf681d7e8ebbba545d5ae6b74b64',
            'https-_csrf': 'R8ZUfQSDav-G52HCcPjAGTVoV7TXPJfAnnxf5axhZNg'
        }
    
    # Generate binary payload
    binary_data, boundary = generate_multipart_binary(pdf_path)
    widget_id = str(uuid.uuid4())
    
    # Build URL
    url = f"https://app.chemscan.de/attachment/create/UUB_Bundle_CadasterBundle_Entity_HazardSubstanceOrganization/{entity_id}"
    
    params = {
        '_widgetContainer': 'dialog',
        '_wid': widget_id,
        '_widgetInit': '1'
    }
    
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'X-CSRF-Header': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }
    
    # Make request with raw binary data
    response = requests.post(
        url,
        params=params,
        data=binary_data,
        headers=headers,
        cookies=cookies
    )
    
    return response


if __name__ == "__main__":
    pdf_path = "001-2024_01040645_Freigabe.pdf"
    
    print("Generating binary multipart data...")
    binary_data, boundary = save_binary_to_file(pdf_path)
    
    print(f"\nFirst 500 bytes:")
    print(binary_data[:500])
    
    print(f"\nLast 100 bytes:")
    print(binary_data[-100:])
    
    # Uncomment to test upload
    # print("\nTesting upload...")
    # response = upload_with_binary(pdf_path)
    # print(f"Response: {response.status_code}")
    # print(f"Content: {response.text[:200]}...")
