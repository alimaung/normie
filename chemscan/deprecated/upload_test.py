import requests
import uuid
import os
from typing import Dict, Any, Optional

def upload_file_to_chemscan(
    file_path: str,
    entity_id: int,
    comment: str,
    owner_id: int,
    csrf_token: str,
    form_token: str,
    cookies: Dict[str, str]
) -> requests.Response:
    """
    Upload a file to ChemScan using direct HTTP request
    
    Args:
        file_path: Path to the file to upload
        entity_id: The entity ID (e.g., 2177 for the chemical substance)
        comment: Comment for the attachment
        owner_id: Owner ID (e.g., 303)
        csrf_token: CSRF token for X-CSRF-Header
        form_token: Form token for oro_attachment[_token]
        cookies: Session cookies as dict
    
    Returns:
        requests.Response object
    """
    
    # Generate random widget ID
    widget_id = str(uuid.uuid4())
    
    # Build URL
    url = f"https://app.chemscan.de/attachment/create/UUB_Bundle_CadasterBundle_Entity_HazardSubstanceOrganization/{entity_id}"
    
    # URL parameters
    params = {
        '_widgetContainer': 'dialog',
        '_wid': widget_id,
        '_widgetInit': '1'
    }
    
    # Prepare file
    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # Form data (matching the PowerShell structure exactly)
    files = {
        'oro_attachment[file][file]': (filename, file_content, 'application/pdf'),
        'oro_attachment[file][emptyFile]': (None, ''),
        'oro_attachment[comment]': (None, comment),
        'oro_attachment[owner]': (None, str(owner_id)),
        'oro_attachment[_token]': (None, form_token),
        '_widgetContainer': (None, 'dialog'),
        '_wid': (None, widget_id),
        '_widgetInit': (None, '0')  # Note: 0 in form data, 1 in URL params
    }
    
    # Headers
    headers = {
        'X-CSRF-Header': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
    }
    
    # Make the request
    response = requests.post(
        url, 
        params=params, 
        files=files, 
        headers=headers, 
        cookies=cookies
    )
    
    return response


def verify_upload_success(
    entity_id: int,
    csrf_token: str,
    cookies: Dict[str, str],
    expected_filename: str
) -> bool:
    """
    Verify upload by checking the attachment grid
    
    Args:
        entity_id: The entity ID
        csrf_token: CSRF token
        cookies: Session cookies
        expected_filename: Filename to look for
    
    Returns:
        True if file appears in attachment grid
    """
    
    # Build the attachment grid URL (from your GET request)
    url = "https://app.chemscan.de/datagrid/attachment-grid"
    
    params = {
        'attachment-grid[entityId]': entity_id,
        'attachment-grid[entityField]': 'hazard_substance_organization_3af9230e',
        'appearanceType': 'grid',
        'attachment-grid[_pager][_page]': 1,
        'attachment-grid[_pager][_per_page]': 25,
        'attachment-grid[_parameters][refresh]': 'true',
        'attachment-grid[_parameters][view]': '__all__',
        'attachment-grid[_appearance][_type]': 'grid',
        'attachment-grid[_columns]': 'originalFilename1.fileSize1.createdAt1.comment1'
    }
    
    headers = {
        'X-CSRF-Header': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json'
    }
    
    response = requests.get(url, params=params, headers=headers, cookies=cookies)
    
    if response.status_code == 200:
        try:
            data = response.json()
            # Look for the filename in the response
            if 'data' in data:
                for item in data['data']:
                    if item.get('originalFilename') == expected_filename:
                        return True
        except:
            pass
    
    return False


# Example usage function
def test_upload():
    """
    Test function - you'll need to fill in your actual values
    """
    
    # Your session data (extract from browser/Selenium)
    cookies = {
        'BAPRM': 'YUtHOFUwTWcxTjduemd1UnA4VHdMTEpMTktXSkdrdjFOUzVWbjc1aVUzOGR3dUlZa1NLa1cxOUNSdmk2aUhSQWtIZDh1T3lremYyTEY3dndsZ2xDcUE9PTptQjFWR3pGbU9HWUtXZHpwKzhVSjZpcXIxYXdmOW1ON0FUdkVrWWt5V2l1TC9BZUljVzNuazJwUkx3RmpBLzErbW9IZHFmTFVYQ2ZkOHYvMTNQQzVGdz09',
        'BAPID': 'e201cf681d7e8ebbba545d5ae6b74b64',
        'https-_csrf': 'R8ZUfQSDav-G52HCcPjAGTVoV7TXPJfAnnxf5axhZNg'
    }
    
    # Test parameters
    file_path = "test_document.pdf"  # Your test file
    entity_id = 2177
    comment = "TEST UPLOAD"
    owner_id = 303
    csrf_token = "R8ZUfQSDav-G52HCcPjAGTVoV7TXPJfAnnxf5axhZNg"
    form_token = "e3c0ece.BjvK3egWitenmERfr5-5vIRVRFyz3MnSLSLyuyOhFWA.R2yb5Nov_OWS33UH_abA69cvDw2Aha-0fA-e6FuTcVlFeJqIh0O-5p_oEQ"
    
    # Upload file
    print(f"Uploading {file_path}...")
    response = upload_file_to_chemscan(
        file_path, entity_id, comment, owner_id, 
        csrf_token, form_token, cookies
    )
    
    print(f"Upload response: {response.status_code}")
    print(f"Response content: {response.text[:200]}...")
    
    # Verify upload
    if response.status_code == 200:
        print("Verifying upload...")
        success = verify_upload_success(
            entity_id, csrf_token, cookies, 
            os.path.basename(file_path)
        )
        print(f"Upload verified: {success}")
    
    return response


if __name__ == "__main__":
    test_upload()
