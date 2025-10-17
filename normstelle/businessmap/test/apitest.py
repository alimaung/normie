import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get API credentials from environment variables
API_KEY = os.getenv('API_KEY')
BOARD_ID = os.getenv('BOARD_ID')
COLUMN_ID = os.getenv('COLUMN_ID')
CARD_ID = os.getenv('CARD_ID')

# Base URL for Kanbanize API
BASE_URL = "https://rollsroyce.kanbanize.com/api/v2"

# Headers for all requests
headers = {
    'accept': 'application/json',
    'apikey': API_KEY,
    'Content-Type': 'application/json'
}

def save_response_to_json(data, filename):
    """Save response data to a JSON file"""
    # Create output directory if it doesn't exist
    output_dir = "businessmap/api_responses"
    os.makedirs(output_dir, exist_ok=True)
    
    # Add timestamp to filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{output_dir}/{timestamp}_{filename}.json"
    
    with open(full_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Response saved to: {full_filename}")
    return full_filename

def make_api_request(endpoint, description, filename, method='GET', json_data=None):
    """Make an API request and save the response to JSON"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n{'='*50}")
    print(f"Making {method} request: {description}")
    print(f"URL: {url}")
    if json_data:
        print(f"Request Body: {json.dumps(json_data, indent=2)}")
    print(f"{'='*50}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=json_data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201, 204]:
            if response.text:  # Some PATCH requests might return empty response
                data = response.json()
            else:
                data = {"success": True, "status_code": response.status_code, "message": "Request completed successfully"}
            saved_file = save_response_to_json(data, filename)
            print(f"✅ Success: Data saved to {saved_file}")
            if isinstance(data, list):
                print(f"Records count: {len(data)}")
        else:
            error_data = {
                "error": True,
                "status_code": response.status_code,
                "response_text": response.text,
                "url": url,
                "method": method,
                "timestamp": datetime.now().isoformat()
            }
            saved_file = save_response_to_json(error_data, f"error_{filename}")
            print(f"❌ Error: {response.status_code}")
            print(f"Error details saved to: {saved_file}")
            
    except requests.exceptions.RequestException as e:
        error_data = {
            "error": True,
            "exception": str(e),
            "url": url,
            "method": method,
            "timestamp": datetime.now().isoformat()
        }
        saved_file = save_response_to_json(error_data, f"exception_{filename}")
        print(f"❌ Request failed: {e}")
        print(f"Exception details saved to: {saved_file}")
    
    return response

def main():
    # Check if required environment variables are set
    if not API_KEY:
        print("Error: API_KEY not found in environment variables")
        print("Please set API_KEY in your .env file")
        return
    
    if not BOARD_ID:
        print("Error: BOARD_ID not found in environment variables")
        print("Please set BOARD_ID in your .env file")
        return
    
    print(f"Using API Key: {API_KEY[:10]}..." if API_KEY else "No API Key")
    print(f"Using Board ID: {BOARD_ID}")
    
    # 1. GET /boards/{board_id}/columns
    #make_api_request(f"/boards/{BOARD_ID}/columns", "Get board columns", "board_columns")
    
    # 2. GET /boards/{board_id} - Get board details
    #make_api_request(f"/boards/{BOARD_ID}", "Get board details", "board_details")
    
    # 3. GET /boards/{board_id}/customFields - Get board custom fields
    #make_api_request(f"/boards/{BOARD_ID}/customFields", "Get board custom fields", "board_custom_fields")
    
    # 4. GET /boards/{board_id}/columns/{column_id} - Get specific column details
    #make_api_request(f"/boards/{BOARD_ID}/columns/{COLUMN_ID}", f"Get column {COLUMN_ID} details", f"column_{COLUMN_ID}_details")
        
    # 6. PATCH /cards/{card_id} - Update specific card
    # Only include fields you want to update, not the entire card object
    #card_update_data = {
    #    "column_id": 206400,  # Moving card to a different column 206400 or 206230
    #}
    
    #make_api_request(f"/cards/{CARD_ID}", f"Update card {CARD_ID}", f"card_{CARD_ID}_update", method='PATCH', json_data=card_update_data)
    
    # 5. GET /cards/{card_id} - Get specific card details
    #make_api_request(f"/cards/{CARD_ID}", f"Get card {CARD_ID} details", f"card_{CARD_ID}_details")
    
    #make_api_request(f"/cards/", f"Get card {CARD_ID} details", f"card_{CARD_ID}_details")
    
    print(f"\n{'='*50}")
    print("All API requests completed!")
    print("Check the 'businessmap/api_responses' directory for saved JSON files.")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
